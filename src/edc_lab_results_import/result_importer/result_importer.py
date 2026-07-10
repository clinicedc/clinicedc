from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from django.conf import settings
from django.core.management import color_style
from parse_trial_labs import parse_folder
from tqdm import tqdm

from edc_reportable.models import NormalData

from ..exceptions import ResultImporterError
from ..models import Result
from ..requisition_resolver import RequisitionResolver
from ..subject_resolver import SubjectResolution, SubjectResolver
from .convert_result import convert_result
from .get_mappings import get_mappings
from .get_parser import get_parser
from .save_summary import SaveSummary
from .unit_conversion import build_normal_data_units_cache
from .utils import to_datetime, to_decimal

__all__ = ["ResultImporter"]


@dataclass(frozen=True)
class UniqueValues:
    order_no: str
    result_no: str
    sample_no: str
    source_utestid: str
    reported_datetime: datetime | None
    name_id: str


class ResultImporter:
    def __init__(
        self,
        laboratory: str,
        path: Path,
        *,
        tz: ZoneInfo | None = None,
        is_valid_identifier_func: Callable | None = None,
        stdout=None,
        dry_run: bool | None = None,
    ) -> None:
        self.df = pd.DataFrame()
        self.laboratory: str = laboratory
        self.is_valid_identifier_func = is_valid_identifier_func
        self.dry_run: bool | None = dry_run
        self.stdout = stdout or sys.stdout
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

    def run(self):
        # build dataframe from PDF file data
        self.df = self.parse_pdfs_to_dataframe()
        # update Result model
        self.dataframe_to_model(self.df, dry_run=self.dry_run)

    def parse_pdfs_to_dataframe(self) -> pd.DataFrame:
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
        return df

    def dataframe_to_model(self, df: pd.DataFrame, *, dry_run: bool | None = None) -> None:
        self.stdout.write(
            f"Resolving source_utestid mappings for laboratory '{self.laboratory}' ...\n"
        )
        if self.dry_run is not None:
            self.dry_run = dry_run
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry run: {len(df)} results parsed, not saved.\n")
            )

        save_summary = self.save_to_results(df)
        save_summary.write_summary(df["source_file"].nunique())

        rr = RequisitionResolver()
        rr.resolve_and_update_results()
        rr.write_summary()

        sys.stdout.flush()

    def save_to_results(self, df: pd.DataFrame, *, batch_size: int = 500) -> SaveSummary:
        """Bulk-create ``Result`` rows from *df*."""
        skipped = 0
        unrecognized_units: set[tuple[str, str]] = set()

        existing_keys = {
            UniqueValues(*row_tuple)
            for row_tuple in Result.objects.values_list(
                "order_no",
                "result_no",
                "sample_no",
                "source_utestid",
                "report_datetime",
                "name_id",
            )
        }
        units_cache = build_normal_data_units_cache()
        imported_results_batch: list[Result] = []
        sr = SubjectResolver()
        for _, row in tqdm(df.iterrows(), total=len(df)):
            name_id = row.get("name_id", "")
            subject_resolution = sr.resolve(
                name_id=name_id,
                subject_identifier=row.get("subject_identifier", ""),
                screening_identifier=row.get("screening_identifier", ""),
            )
            unique_values = UniqueValues(
                row.get("order_no", ""),
                row.get("result_no", ""),
                row.get("sample_no", ""),
                row.get("source_utestid", ""),
                to_datetime(row.get("reported_datetime")),
                name_id,
            )
            if unique_values in existing_keys:
                skipped += 1
                continue

            existing_keys.add(unique_values)

            result_value = to_decimal(row.get("result", ""))

            utestid = row.get("utestid", "")
            units = row.get("units", "")
            converted_value, converted_units = convert_result(
                utestid, result_value, units, units_cache, unrecognized_units
            )

            imported_results_batch.append(
                self.prepare_imported_result(
                    unique_values,
                    row,
                    subject_resolution,
                    subject_resolution.match_category,
                    subject_resolution.match_comment,
                    utestid,
                    result_value,
                    units,
                    converted_value,
                    converted_units,
                )
            )
            if not self.dry_run and len(imported_results_batch) >= batch_size:
                Result.objects.bulk_create(imported_results_batch)
                imported_results_batch.clear()

        if not self.dry_run and imported_results_batch:
            Result.objects.bulk_create(imported_results_batch)

        return SaveSummary(
            created=len(df) - skipped,
            skipped=skipped,
            unresolved=sr.unresolved_count,
            subject_not_found=sr.subject_not_found_count,
            reasons=sr.reasons,
            unrecognized_units=unrecognized_units,
            stdout=self.stdout,
            style=self.style,
        )

    def prepare_imported_result(
        self,
        unique_values: UniqueValues,
        row: pd.Series,
        resolution: SubjectResolution,
        match_category: str,
        match_comment: str,
        utestid: str,
        result_value: Decimal | None,
        units: str,
        converted_value: Decimal | None,
        converted_units: str,
    ) -> Result:
        return Result(
            laboratory=self.laboratory,
            order_no=unique_values.order_no,
            result_no=unique_values.result_no,
            sample_no=unique_values.sample_no,
            source_utestid=unique_values.source_utestid,
            report_datetime=unique_values.reported_datetime,
            name_id=unique_values.name_id,
            subject_identifier=resolution.subject_identifier,
            screening_identifier=resolution.screening_identifier,
            subject_not_found=not resolution.resolved,
            requisition_match_category=match_category,
            requisition_match_comment=match_comment,
            utestid=utestid,
            source_file=row.get("source_file", ""),
            report_type=row.get("report_type", ""),
            result_status=row.get("result_status", ""),
            age=(int(row["age"]) if row.get("age") else None),
            sex=row.get("sex", ""),
            ordered_by=row.get("ordered_by", ""),
            clinic_ward=row.get("clinic_ward", ""),
            order_datetime=to_datetime(row.get("order_datetime")),
            result_datetime=to_datetime(row.get("result_datetime")),
            specimen_collected_by=row.get("specimen_collected_by", ""),
            specimen_collected_datetime=to_datetime(row.get("specimen_collected_datetime")),
            specimen_received_by=row.get("specimen_received_by", ""),
            specimen_received_datetime=to_datetime(row.get("specimen_received_datetime")),
            sample_type=row.get("sample_type", ""),
            sample_condition=row.get("sample_condition", ""),
            priority=row.get("priority", ""),
            reported_by=row.get("reported_by", ""),
            verified_by=row.get("verified_by", ""),
            verified_datetime=to_datetime(row.get("verified_datetime")),
            result_value=result_value,
            units=units,
            converted_result_value=converted_value,
            converted_units=converted_units,
            flag=row.get("flag", ""),
            reference_range_lower=to_decimal(row.get("reference_range_lower", "")),
            reference_range_upper=to_decimal(row.get("reference_range_upper", "")),
        )
