from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pandas as pd
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import color_style
from django_pandas.io import read_frame
from parse_trial_labs import parse_folder
from tqdm import tqdm

from edc_appointment.constants import ONTIME_APPT
from edc_lab.constants import FINGER_PRICK
from edc_lab.site_labs import site_labs
from edc_lab_panel.constants import (
    BASOPHILS,
    BASOPHILS_DIFF,
    EOSINOPHILS,
    EOSINOPHILS_DIFF,
    MONOCYTES,
    MONOCYTES_DIFF,
)
from edc_registration.models import RegisteredSubject
from edc_reportable.models import NormalData

from ..exceptions import ResultImporterError
from .get_mappings import get_mappings
from .get_parser import get_parser
from .save_summary import SaveSummary
from .utils import to_datetime, to_decimal, to_int, to_pk, to_str

if TYPE_CHECKING:
    from edc_lab import RequisitionPanel

    from ..models import Result

__all__ = ["ResultImporter"]


@dataclass(frozen=True)
class UniqueValues:
    order_no: str
    result_no: str
    sample_no: str
    result_status: str
    source_utestid: str
    utestid: str
    result_datetime: datetime | None
    name_id: str


class ResultImporter:
    """
    Parse results from a folder of PDFs and import data into
    the Result model.

    For example:
        # instantiate
        importer = ResultImporter(
            "MNH",
            Path("~/upload/gmail").expanduser(),
            is_valid_identifier_func=is_valid_subject_identifier,
            extra_panels=[wbc_differential],
        )
        # create the dataframe (importer.df)
        importer.run()
        # import the df into Result. Manually clear the Result
        # table before this step.
        importer.dataframe_to_model(importer.df)

    """

    def __init__(
        self,
        laboratory: str,
        path: Path,
        *,
        tz: ZoneInfo | None = None,
        is_valid_identifier_func: Callable | None = None,
        stdout=None,
        dry_run: bool | None = None,
        extra_panels: list[RequisitionPanel] | None = None,
    ) -> None:
        self._df_utestid = pd.DataFrame()
        self._df_requisitions = pd.DataFrame()
        self._df_related_visit = pd.DataFrame()
        self._df_screening = pd.DataFrame()
        self._df_registered_subject = pd.DataFrame()
        self.df = pd.DataFrame()
        self.laboratory: str = laboratory
        self.is_valid_identifier_func = is_valid_identifier_func
        self.dry_run: bool | None = dry_run
        self.stdout = stdout or sys.stdout
        self.extra_panels: list[RequisitionPanel] = extra_panels or []
        self.style = color_style()
        self.tz = tz or ZoneInfo(settings.TIME_ZONE)
        self.known_utestids = set(
            NormalData.objects.values_list("label", flat=True).distinct()
        )
        mappings: dict[str, dict[str, str]] = get_mappings(self.laboratory)
        self.utestid_mappings = mappings["UTESTIDS"]
        self.unit_mappings = mappings["UNITS"]
        self.path = Path(path).expanduser()
        if not path.is_dir():
            raise ResultImporterError(f"Not a directory: {path}")

    def run(self, to_model: bool | None = None, df_to_path: Path | None = None):
        # build dataframe from PDF file data
        self.parse_pdfs_to_dataframe()
        if df_to_path:
            self.write_df_to_parquet(df_to_path, "raw_")
        self.stdout.write(f"parse_pdfs_to_dataframe: {len(self.df)}\n")
        self.resolve()
        self.stdout.write(f"resolve: {len(self.df)}\n")
        self.apply_unit_mapping()
        self.stdout.write(f"apply_unit_mapping: {len(self.df)}\n")
        if df_to_path:
            self.write_df_to_parquet(df_to_path)
        # update Result model
        if to_model:
            self.dataframe_to_model(self.df, dry_run=self.dry_run)

    def write_df_to_parquet(self, df_to_path, name_suffix: str | None = None):
        name_suffix = "" if name_suffix is None else name_suffix
        if not df_to_path.exists():
            raise ValueError("Path does not exist. Got {df_to_path}.")
        fname = (
            f"results_importer_{name_suffix}"
            f"{datetime.now(tz=ZoneInfo('UTC')).strftime('%Y%m%d%H%M')}.parquet"
        )
        self.df.to_parquet(df_to_path / fname, index=False)
        self.stdout.write(self.style.SUCCESS(f"Dataframe written to {fname}\n"))

    def parse_pdfs_to_dataframe(self):
        """Parse PDF files into a dataframe."""
        pdf_count = len(list(self.path.glob("*.pdf")))
        if pdf_count == 0:
            raise ResultImporterError(f"No PDF files found in {self.path}")

        parser_func = get_parser(self.laboratory)
        df: pd.DataFrame = parse_folder(
            self.path,
            parser_func,
            tz=self.tz,
            is_valid_identifier_func=self.is_valid_identifier_func,
        )
        df["utestid"] = df["source_utestid"].map(self.utestid_mappings)
        df["units"] = df["source_units"].map(self.unit_mappings).fillna(df["source_units"])
        df["order_datetime"] = pd.to_datetime(df["order_datetime"], utc=True).dt.normalize()
        df["specimen_collected_datetime"] = pd.to_datetime(
            df["specimen_collected_datetime"], utc=True
        ).dt.normalize()
        for col in [
            "subject_identifier",
            "screening_identifier",
            "source_utestid",
            "utestid",
            "source_units",
            "units",
            "report_type",
            "result_status",
            "order_no",
            "sample_no",
            "result_no",
            "name_id",
        ]:
            df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
        self.df = df

    def resolve(self):
        expected_len = len(self.df)
        self.df = self.df.merge(self.df_utestid, on="utestid", how="left").reset_index(
            drop=True
        )
        self._assert_row_count(expected_len, "merge with df_utestid")
        self.resolve_requisitions()
        self._assert_row_count(expected_len, "resolve_requisitions")
        self.resolve_related_visits()
        self._assert_row_count(expected_len, "resolve_related_visits")
        self.resolve_sites()
        self._assert_row_count(expected_len, "resolve_sites")
        self.apply_unit_mapping()

    def _assert_row_count(self, expected_len: int, step: str) -> None:
        if len(self.df) != expected_len:
            raise ResultImporterError(
                f"{step} introduced duplicate rows via a fan-out merge. "
                f"Expected {expected_len} rows, got {len(self.df)}."
            )

    def apply_unit_mapping(self):
        UNIT_MAPPINGS: dict[str, str] = {  # noqa: N806
            "U/L": "IU/L",
            "K/uL": "10^9/L",
            "k/uL": "10^9/L",
            "10*3/uL": "10^3/L",
            "10*9/L": "10^9/L",
            "fL": "fL/cell",
            "pg": "pg/cell",
            "µmol/L": "umol/L",
            "μmol/L": "umol/L",
        }
        self.df["units"] = self.df["units"].replace(UNIT_MAPPINGS)

    def dataframe_to_model(
        self,
        df: pd.DataFrame,
        *,
        dry_run: bool | None = None,
        batch_size: int | None = None,
    ) -> None:
        batch_size = batch_size or 500
        if self.dry_run is not None:
            self.dry_run = dry_run
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry run: {len(df)} results parsed, not saved.\n")
            )
        self.stdout.write("Writing dataframe to Result model ...\n")
        save_summary = self.save_to_model(df, batch_size=batch_size)
        file_count = 0 if df.empty else df["source_file"].nunique()
        save_summary.write_summary(file_count)
        sys.stdout.flush()

    def model_to_dataframe(self) -> pd.DataFrame:
        df = read_frame(self.result_model_cls.objects.all(), verbose=False)
        for col in [
            "subject_visit",
            "requisition",
            "subject_identifier",
            "screening_identifier",
            "requisition_identifier",
            "requisition_match_category",
            "requisition_match_comment",
            "visit_code",
            "panel_name",
            "laboratory",
            "source_file",
            "source_utestid",
            "utestid",
            "source_units",
            "units",
            "converted_units",
            "report_type",
            "result_status",
            "order_no",
            "ordered_by",
            "sample_no",
            "result_no",
            "name_id",
            "sex",
            "clinic_ward",
            "specimen_collected_by",
            "specimen_received_by",
            "sample_type",
            "sample_condition",
            "priority",
            "reported_by",
            "verified_by",
            "flag",
        ]:
            df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
        for col in ["age", "visit_code_sequence"]:
            df[col] = df[col].astype("Int64")
        for col in [
            "result_value",
            "converted_result_value",
            "reference_range_lower",
            "reference_range_upper",
        ]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
        for col in ["subject_not_found", "requisition_ambiguous"]:
            df[col] = df[col].astype("bool")
        for col in [
            "order_datetime",
            "report_datetime",
            "result_datetime",
            "specimen_collected_datetime",
            "specimen_received_datetime",
            "reported_datetime",
            "verified_datetime",
            "transcribed_datetime",
        ]:
            df[col] = pd.to_datetime(df[col], utc=True)
        return df

    @property
    def result_model_cls(self):
        return django_apps.get_model("edc_lab_results_import.result")

    @property
    def df_utestid(self) -> pd.DataFrame:
        records: list[tuple[str, str]] = []
        if self._df_utestid.empty:
            # temp until parsing utestid map is updated
            self.df.loc[self.df["utestid"] == "mono#", "utestid"] = MONOCYTES
            self.df.loc[self.df["utestid"] == "mono%", "utestid"] = MONOCYTES_DIFF
            self.df.loc[self.df["utestid"] == "eos#", "utestid"] = EOSINOPHILS
            self.df.loc[self.df["utestid"] == "eos%", "utestid"] = EOSINOPHILS_DIFF
            self.df.loc[self.df["utestid"] == "baso#", "utestid"] = BASOPHILS
            self.df.loc[self.df["utestid"] == "baso%", "utestid"] = BASOPHILS_DIFF
            for lab_profile in site_labs.lab_profiles.values():
                for panel in lab_profile.panels.values():
                    for utestid in panel.flatten_utestids():
                        records.append((utestid, panel.name))  # noqa: PERF401
            for panel in self.extra_panels:
                for utestid in panel.flatten_utestids():
                    records.append((utestid, panel.name))  # noqa: PERF401
            self._df_utestid = pd.DataFrame(
                records, columns=["utestid", "panel_name"]
            ).drop_duplicates()
            if not self._df_utestid.utestid.is_unique:
                raise ValueError("Utestid column must be unique.")
            self._df_utestid["utestid"] = (
                self._df_utestid["utestid"].astype("string").fillna(pd.NA)
            )
            self._df_utestid["panel_name"] = (
                self._df_utestid["panel_name"].astype("string").fillna(pd.NA)
            )
        return self._df_utestid

    @property
    def df_requisitions(self) -> pd.DataFrame:
        if self._df_requisitions.empty:
            requisition_model_cls = django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)
            df = read_frame(
                requisition_model_cls.objects.values(
                    "id",
                    "subject_identifier",
                    "subject_visit",
                    "subject_visit__visit_code",
                    "subject_visit__visit_code_sequence",
                    "requisition_identifier",
                    "report_datetime",
                    "drawn_datetime",
                    "panel__name",
                )
                .filter(drawn_datetime__isnull=False)
                .exclude(item_type=FINGER_PRICK),
                verbose=False,
            ).rename(
                columns={
                    "id": "requisition",
                    "report_datetime": "requisition_datetime",
                    "subject_visit_id": "subject_visit",
                    "subject_visit__visit_code": "visit_code",
                    "subject_visit__visit_code_sequence": "visit_code_sequence",
                    "panel__name": "panel_name",
                }
            )
            df["requisition_datetime"] = pd.to_datetime(
                df["requisition_datetime"], utc=True
            ).dt.normalize()
            df["drawn_datetime"] = pd.to_datetime(
                df["drawn_datetime"], utc=True
            ).dt.normalize()
            df["subject_identifier"] = df["subject_identifier"].astype("string").fillna(pd.NA)
            df["requisition_identifier"] = (
                df["requisition_identifier"].astype("string").fillna(pd.NA)
            )
            df["requisition"] = df["requisition"].astype("string").fillna(pd.NA)
            df["subject_visit"] = df["subject_visit"].astype("string").fillna(pd.NA)

            df = df.merge(self.df_utestid, on="panel_name", how="left")
            self._df_requisitions = (
                df.sort_values("visit_code_sequence")
                .drop_duplicates(
                    subset=["subject_identifier", "visit_code", "drawn_datetime", "utestid"],
                    keep="first",
                )
                .reset_index(drop=True)
            )
        return self._df_requisitions

    @property
    def df_related_visits(self) -> pd.DataFrame:
        if self._df_related_visit.empty:
            schedule_name = "schedule"
            related_visit_model_cls = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
            df = read_frame(
                related_visit_model_cls.objects.values(
                    "id",
                    "appointment__subject_identifier",
                    "report_datetime",
                    "visit_code",
                    "visit_code_sequence",
                    "schedule_name",
                ).filter(appointment__appt_timing=ONTIME_APPT),
                verbose=False,
            ).rename(
                columns={
                    "id": "subject_visit",
                    "report_datetime": "visit_datetime",
                    "appointment__subject_identifier": "subject_identifier",
                }
            )
            df["subject_visit"] = df["subject_visit"].astype("string").fillna(pd.NA)
            df["subject_identifier"] = df["subject_identifier"].astype("string").fillna(pd.NA)
            df["visit_code"] = df["visit_code"].astype("string").fillna(pd.NA)
            df["visit_code_sequence"] = df["visit_code_sequence"].astype("Int64").fillna(pd.NA)

            df = df[df["schedule_name"] == schedule_name]
            if (
                df[df["schedule_name"] == "schedule"]
                .duplicated(subset=["subject_identifier", "visit_datetime"])
                .any()
            ):
                raise ValueError

            df["visit_datetime"] = pd.to_datetime(
                df["visit_datetime"], utc=True
            ).dt.normalize()
            self._df_related_visit = df.copy().reset_index(drop=True)
        return self._df_related_visit

    @property
    def df_screening(self) -> pd.DataFrame:
        if self._df_screening.empty:
            screening_model_cls = django_apps.get_model(settings.SUBJECT_SCREENING_MODEL)
            df = read_frame(
                screening_model_cls.objects.values("screening_identifier", "site").all(),
                verbose=False,
            )
            df["screening_identifier"] = (
                df["screening_identifier"].astype("string").fillna(pd.NA)
            )
            df["site"] = df["site"].astype("string").fillna(pd.NA)
            self._df_screening = df
        return self._df_screening

    @property
    def df_registered_subject(self) -> pd.DataFrame:
        if self._df_registered_subject.empty:
            df = read_frame(
                RegisteredSubject.objects.values("subject_identifier", "site").all(),
                verbose=False,
            )
            df["subject_identifier"] = df["subject_identifier"].astype("string").fillna(pd.NA)
            df["site"] = df["site"].astype("string").fillna(pd.NA)
            self._df_registered_subject = df
        return self._df_registered_subject

    def resolve_requisitions(self):
        remaining = self.df.copy()
        results = []
        suffixes = ("", "_right")
        key_sets = [
            ["subject_identifier", "specimen_collected_datetime", "utestid"],
            ["subject_identifier", "order_datetime", "utestid"],
        ]
        for datecol in ["drawn_datetime", "requisition_datetime"]:
            for keys in key_sets:
                merged = remaining.merge(
                    self.df_requisitions,
                    left_on=keys,
                    right_on=["subject_identifier", datecol, "utestid"],
                    how="left",
                    indicator=True,
                    suffixes=suffixes,
                )
                matched = merged[merged["_merge"] == "both"].drop(columns="_merge")
                results.append(matched)
                remaining = merged.loc[merged["_merge"] == "left_only", remaining.columns]
        results.append(remaining)
        self.df = pd.concat(results)
        self.df = self.df.drop(
            columns=[c for c in self.df.columns if c.endswith("_right")]
        ).sort_index()

    def resolve_related_visits(self):
        already_matched = self.df[~self.df["subject_visit"].isna()].copy()
        remaining = self.df[self.df["subject_visit"].isna()].copy()
        results = []
        df_related_visits = self.df_related_visits
        suffixes = ("", "_right")
        key_sets = [
            ["subject_identifier", "specimen_collected_datetime"],
            ["subject_identifier", "order_datetime"],
        ]
        for keys in key_sets:
            merged = remaining.merge(
                df_related_visits,
                left_on=keys,
                right_on=["subject_identifier", "visit_datetime"],
                how="left",
                indicator=True,
                suffixes=suffixes,
            )
            matched = merged[merged["_merge"] == "both"].drop(columns="_merge")
            results.append(matched)
            remaining = merged.loc[merged["_merge"] == "left_only", remaining.columns]
        results.append(remaining)
        results.append(already_matched)
        df_result = pd.concat(results)
        df_result = df_result.reset_index(drop=True)
        df_result.loc[
            (df_result["subject_visit"].isna()) & ~(df_result["subject_visit_right"].isna()),
            "subject_visit",
        ] = df_result["subject_visit_right"]

        df_result = df_result.set_index("subject_visit")
        df_related_visits = df_related_visits.set_index("subject_visit")
        df_result.update(
            df_related_visits[["visit_code", "visit_code_sequence", "visit_datetime"]],
            overwrite=False,
        )
        self.df = df_result.reset_index()

    def resolve_sites(self):
        self.df = self.df.merge(
            self.df_screening, on="screening_identifier", how="left"
        ).reset_index(drop=True)
        self.df = self.df.merge(
            self.df_registered_subject, on="subject_identifier", how="left"
        ).reset_index(drop=True)
        self.df["site"] = pd.NA
        self.df.loc[self.df["site_x"].isna(), "site"] = self.df["site_y"]
        self.df.loc[self.df["site_y"].isna(), "site"] = self.df["site_x"]
        self.df = self.df.drop(columns=["site_x", "site_y"])

    def save_to_model(self, df: pd.DataFrame, *, batch_size: int | None = None) -> SaveSummary:
        """Bulk-create ``Result`` rows from *df*."""
        batch_size = batch_size or 500
        skipped = 0
        imported_results_batch: list[Result] = []

        existing_keys = {
            UniqueValues(*row_tuple)
            for row_tuple in self.result_model_cls.objects.values_list(
                "order_no",
                "result_no",
                "sample_no",
                "result_status",
                "source_utestid",
                "utestid",
                "result_datetime",
                "name_id",
            )
        }
        for _, row in tqdm(df.iterrows(), total=len(df)):
            name_id = to_str(row.get("name_id", ""))
            unique_values = UniqueValues(
                to_str(row.get("order_no", "")),
                to_str(row.get("result_no", "")),
                to_str(row.get("sample_no", "")),
                to_str(row.get("result_status", "")),
                to_str(row.get("source_utestid", "")),
                to_str(row.get("utestid", "")),
                to_datetime(row.get("result_datetime")),
                name_id,
            )
            if unique_values in existing_keys:
                skipped += 1
                continue

            existing_keys.add(unique_values)
            if batch_size == 1:
                try:
                    self.result_model_cls.objects.get(**asdict(unique_values))
                except ObjectDoesNotExist:
                    pass
                else:
                    skipped += 1
                    existing_keys.add(unique_values)
                    continue
            imported_results_batch.append(self.prepare_imported_result(unique_values, row))
            if len(imported_results_batch) >= batch_size:
                self.result_model_cls.objects.bulk_create(imported_results_batch)
                imported_results_batch.clear()

        if not self.dry_run and imported_results_batch:
            self.result_model_cls.objects.bulk_create(imported_results_batch)

        return SaveSummary(
            created=len(df) - skipped, skipped=skipped, stdout=self.stdout, style=self.style
        )

    def prepare_imported_result(
        self,
        unique_values: UniqueValues,
        row: pd.Series,
    ) -> Result:
        return self.result_model_cls(
            laboratory=self.laboratory,
            order_no=unique_values.order_no,
            result_no=unique_values.result_no,
            sample_no=unique_values.sample_no,
            result_status=unique_values.result_status,
            source_utestid=unique_values.source_utestid,
            utestid=unique_values.utestid,
            result_datetime=unique_values.result_datetime,
            name_id=unique_values.name_id,
            subject_identifier=to_str(row.get("subject_identifier", "")),
            screening_identifier=to_str(row.get("screening_identifier", "")),
            subject_visit_id=to_pk(row.get("subject_visit")),
            requisition_id=to_pk(row.get("requisition")),
            source_file=to_str(row.get("source_file", "")),
            report_type=to_str(row.get("report_type", "")),
            age=to_int(row.get("age")),
            sex=to_str(row.get("sex", "")),
            ordered_by=to_str(row.get("ordered_by", "")),
            clinic_ward=to_str(row.get("clinic_ward", "")),
            order_datetime=to_datetime(row.get("order_datetime")),
            report_datetime=to_datetime(row.get("report_datetime")),
            specimen_collected_by=to_str(row.get("specimen_collected_by", "")),
            specimen_collected_datetime=to_datetime(row.get("specimen_collected_datetime")),
            specimen_received_by=to_str(row.get("specimen_received_by", "")),
            specimen_received_datetime=to_datetime(row.get("specimen_received_datetime")),
            sample_type=to_str(row.get("sample_type", "")),
            sample_condition=to_str(row.get("sample_condition", "")),
            priority=to_str(row.get("priority", "")),
            reported_by=to_str(row.get("reported_by", "")),
            verified_by=to_str(row.get("verified_by", "")),
            verified_datetime=to_datetime(row.get("verified_datetime")),
            result_value=to_decimal(row.get("result")),
            units=to_str(row.get("units", "")),
            flag=to_str(row.get("flag", "")),
            reference_range_lower=to_decimal(row.get("reference_range_lower")),
            reference_range_upper=to_decimal(row.get("reference_range_upper")),
        )
