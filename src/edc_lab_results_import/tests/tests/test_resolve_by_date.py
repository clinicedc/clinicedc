from __future__ import annotations

from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pandas as pd
from django.core.management import color_style
from django.test import SimpleTestCase, tag

from edc_lab.constants import FINGER_PRICK
from edc_lab_results_import.result_importer.result_importer import ResultImporter

MODULE = "edc_lab_results_import.result_importer.result_importer"
TZ = ZoneInfo("Africa/Dar_es_Salaam")
SUBJECT = "101-00000001-1"
SCREENING = "S0000001"
VISIT_1000 = "visit-1000"
VISIT_1010 = "visit-1010"
REQ_FBC = "req-fbc"
BASELINE = datetime(2025, 3, 3, 9, 0, tzinfo=TZ)
FOLLOWUP = datetime(2025, 4, 3, 9, 0, tzinfo=TZ)


def make_requisition_df(**kwargs) -> pd.DataFrame:
    """Shaped like `get_requisition_df`, one FBC requisition at
    baseline, drawn at 08:00 and keyed at 08:05.
    """
    df = pd.DataFrame(
        {
            "requisition": [REQ_FBC],
            "subject_identifier": [SUBJECT],
            "subject_visit": [VISIT_1000],
            "visit_code": [1000.0],
            "visit_code_str": ["1000"],
            "visit_code_sequence": [0],
            "visit_datetime": [BASELINE],
            "requisition_identifier": ["ABC1234"],
            "requisition_datetime": [BASELINE.replace(hour=8, minute=5)],
            "drawn_datetime": [BASELINE.replace(hour=8)],
            "panel_name": ["fbc"],
            "utestid": ["haemoglobin"],
        }
    ).astype(
        {
            "requisition": "string",
            "subject_identifier": "string",
            "subject_visit": "string",
            "panel_name": "string",
            "utestid": "string",
        }
    )
    for col in ["visit_datetime", "requisition_datetime", "drawn_datetime"]:
        df[col] = pd.to_datetime(df[col], utc=True)
    return df


def make_parsed_row(
    specimen_collected_datetime: datetime | None,
    *,
    utestid: str = "haemoglobin",
    subject_identifier: str | None = SUBJECT,
    screening_identifier: str | None = None,
    order_datetime: datetime | None = None,
) -> dict:
    """A row as `parse_folder` returns it after `apply_mappings_after_parse`."""
    return dict(
        subject_identifier=subject_identifier,
        screening_identifier=screening_identifier,
        source_utestid=utestid.upper(),
        utestid=utestid,
        source_units="g/dL",
        units="g/dL",
        report_type="final",
        result_status="final",
        order_no="ORD001",
        sample_no="SAM001",
        result_no=f"RES-{utestid}",
        name_id="NAME001",
        order_datetime=order_datetime,
        specimen_collected_datetime=specimen_collected_datetime,
    )


@tag("lab_results_import")
@patch(f"{MODULE}.get_requisition_panel_name_map", return_value={})
@patch(f"{MODULE}.get_requisition_df", side_effect=make_requisition_df)
class TestResolveByDate(SimpleTestCase):
    """The lab reports when a specimen was collected, the EDC records
    when it was drawn and when the visit was reported. The two never
    agree to the second, so requisitions and visits are matched by day
    in the local time zone.

    Matching on the full datetimes linked no result to a requisition or
    a visit at all.
    """

    def make_importer(self, rows: list[dict]) -> ResultImporter:
        """Builds a `ResultImporter` without `__init__`, which wants a
        real PDF folder and laboratory mapping files. See
        `test_result_importer_roundtrip`.
        """
        importer = ResultImporter.__new__(ResultImporter)
        importer.stdout = StringIO()
        importer.style = color_style()
        importer.tz = TZ
        importer.max_days_before_baseline = 30
        importer._df_requisitions = pd.DataFrame()
        importer._df_utestid = pd.DataFrame(
            [("haemoglobin", "fbc"), ("creatinine", "chemistry")],
            columns=["utestid", "panel_name"],
        ).astype("string")
        importer._df_related_visit = self.make_df_related_visits(importer)
        importer._df_screening = pd.DataFrame(
            {"screening_identifier": [SCREENING], "site": ["10"]}
        ).astype("string")
        importer._df_registered_subject = pd.DataFrame(
            {
                "subject_identifier": [SUBJECT],
                "screening_identifier": [SCREENING],
                "site": ["10"],
            }
        ).astype("string")
        importer.df = pd.DataFrame(rows)
        importer.update_dtypes_after_parse()
        return importer

    @staticmethod
    def make_df_related_visits(importer: ResultImporter) -> pd.DataFrame:
        """Shaped like `ResultImporter.df_related_visits`, which reads
        from the database.
        """
        df = pd.DataFrame(
            {
                "subject_visit": [VISIT_1000, VISIT_1010],
                "subject_identifier": [SUBJECT, SUBJECT],
                "visit_datetime": [BASELINE, FOLLOWUP],
                "visit_code": ["1000", "1010"],
                "visit_code_sequence": [0, 0],
                "schedule_name": ["schedule", "schedule"],
            }
        ).astype(
            {
                "subject_visit": "string",
                "subject_identifier": "string",
                "visit_code": "string",
                "visit_code_sequence": "Int64",
            }
        )
        df["visit_datetime"] = pd.to_datetime(df["visit_datetime"], utc=True)
        df["visit_date"] = importer.to_local_date(df["visit_datetime"])
        return df

    def resolve(self, *rows: dict) -> pd.DataFrame:
        importer = self.make_importer(list(rows))
        importer.resolve()
        return importer.df

    def test_links_requisition_drawn_earlier_on_the_same_day(self, *mocks):  # noqa: ARG002
        df = self.resolve(make_parsed_row(BASELINE.replace(hour=10, minute=15)))
        self.assertEqual(df.iloc[0]["requisition"], REQ_FBC)
        self.assertEqual(df.iloc[0]["subject_visit"], VISIT_1000)

    def test_links_requisition_by_order_datetime(self, *mocks):  # noqa: ARG002
        df = self.resolve(
            make_parsed_row(None, order_datetime=BASELINE.replace(hour=11, minute=40))
        )
        self.assertEqual(df.iloc[0]["requisition"], REQ_FBC)

    def test_does_not_link_requisition_on_another_day(self, *mocks):  # noqa: ARG002
        df = self.resolve(make_parsed_row(BASELINE + timedelta(days=1)))
        self.assertTrue(pd.isna(df.iloc[0]["requisition"]))

    def test_the_day_is_taken_in_the_local_time_zone(self, *mocks):  # noqa: ARG002
        """Collected 01:30 local, 22:30 UTC the day before. By the UTC
        day it would miss the requisition drawn that morning.
        """
        df = self.resolve(make_parsed_row(BASELINE.replace(hour=1, minute=30)))
        self.assertEqual(df.iloc[0]["requisition"], REQ_FBC)

    def test_links_visit_on_the_same_day_without_a_requisition(self, *mocks):  # noqa: ARG002
        df = self.resolve(
            make_parsed_row(FOLLOWUP.replace(hour=14), utestid="creatinine"),
        )
        self.assertTrue(pd.isna(df.iloc[0]["requisition"]))
        self.assertEqual(df.iloc[0]["subject_visit"], VISIT_1010)
        self.assertEqual(df.iloc[0]["visit_code"], "1010")

    def test_screening_specimen_is_linked_to_baseline(self, *mocks):  # noqa: ARG002
        """Reported with only a screening identifier. The subject is
        resolved before the visit passes, which match on it.
        """
        df = self.resolve(
            make_parsed_row(
                BASELINE - timedelta(days=5),
                utestid="creatinine",
                subject_identifier=None,
                screening_identifier=SCREENING,
            )
        )
        self.assertEqual(df.iloc[0]["subject_identifier"], SUBJECT)
        self.assertEqual(df.iloc[0]["subject_visit"], VISIT_1000)

    def test_site_is_kept_where_both_identifiers_are_known(self, *mocks):  # noqa: ARG002
        df = self.resolve(
            make_parsed_row(
                BASELINE.replace(hour=10),
                subject_identifier=None,
                screening_identifier=SCREENING,
            )
        )
        self.assertEqual(df.iloc[0]["site"], "10")

    def test_datetimes_are_kept_whole(self, *mocks):  # noqa: ARG002
        """Only the join keys are dates. `Result` stores the datetimes."""
        collected = BASELINE.replace(hour=10, minute=15)
        df = self.resolve(make_parsed_row(collected))
        self.assertEqual(
            df.iloc[0]["specimen_collected_datetime"],
            pd.Timestamp(collected).tz_convert("UTC"),
        )

    def test_finger_prick_requisitions_are_excluded(self, get_requisition_df, *mocks):  # noqa: ARG002
        self.resolve(make_parsed_row(BASELINE.replace(hour=10)))
        get_requisition_df.assert_called_once_with(exclude_item_types=[FINGER_PRICK])

    def test_visit_code_from_requisition_is_the_string(self, *mocks):  # noqa: ARG002
        """`get_requisition_df` has a float `visit_code`, which would be
        saved to `Result.visit_code` as "1000.0".
        """
        df = self.resolve(make_parsed_row(BASELINE.replace(hour=10)))
        self.assertEqual(df.iloc[0]["visit_code"], "1000")
