from __future__ import annotations

from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

import pandas as pd
from django.core.management import color_style
from django.test import TestCase, tag

from edc_lab_results_import.models import Result
from edc_lab_results_import.result_importer.result_importer import ResultImporter, UniqueValues
from edc_lab_results_import.result_importer.utils import to_datetime, to_str

UTC = ZoneInfo("UTC")

STRING_COLS = [
    "subject_identifier",
    "screening_identifier",
    "source_utestid",
    "utestid",
    "units",
    "sex",
    "ordered_by",
    "clinic_ward",
    "flag",
    "source_file",
]
INT_COLS = ["age", "visit_code_sequence"]
DECIMAL_COLS = [
    "result_value",
    "converted_result_value",
    "reference_range_lower",
    "reference_range_upper",
]
BOOL_COLS = ["subject_not_found", "requisition_ambiguous"]
DATETIME_COLS = [
    "order_datetime",
    "report_datetime",
    "specimen_collected_datetime",
    "specimen_received_datetime",
    "verified_datetime",
]


def make_importer() -> ResultImporter:
    """Builds a `ResultImporter` without running `__init__`, which requires
    a real PDF folder, laboratory-specific utestid/unit mapping files, and
    `NormalData` fixtures unrelated to the dataframe <-> model round trip
    exercised here.
    """
    importer = ResultImporter.__new__(ResultImporter)
    importer.laboratory = "MNH"
    importer.dry_run = False
    importer.stdout = StringIO()
    importer.style = color_style()
    return importer


@tag("lab_results_import")
class TestResultImporterDataframeRoundTrip(TestCase):
    def setUp(self):
        self.importer = make_importer()

    def build_source_df(self) -> pd.DataFrame:
        full_row = {
            "order_no": "ORD001",
            "result_no": "RES001",
            "sample_no": "SAM001",
            "result_status": "final",
            "source_utestid": "HGB",
            "utestid": "haemoglobin",
            "result_datetime": datetime(2026, 1, 5, 9, 0, tzinfo=UTC),
            "name_id": "NAME001",
            "subject_identifier": "101-40990001-6",
            "screening_identifier": "SCR0001",
            "subject_visit": None,
            "requisition": None,
            "source_file": "report_001.pdf",
            "report_type": "haematology",
            "age": 34,
            "sex": "M",
            "ordered_by": "Dr Jones",
            "clinic_ward": "OPD",
            "order_datetime": datetime(2026, 1, 5, tzinfo=UTC),
            "report_datetime": datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
            "specimen_collected_by": "Nurse A",
            "specimen_collected_datetime": datetime(2026, 1, 5, tzinfo=UTC),
            "specimen_received_by": "Lab Tech B",
            "specimen_received_datetime": datetime(2026, 1, 5, 8, 45, tzinfo=UTC),
            "sample_type": "whole blood",
            "sample_condition": "acceptable",
            "priority": "routine",
            "reported_by": "Dr Smith",
            "verified_by": "Dr Verify",
            "verified_datetime": datetime(2026, 1, 5, 11, 0, tzinfo=UTC),
            "result": 13.4,
            "units": "g/dL",
            "flag": "H",
            "reference_range_lower": 12.0,
            "reference_range_upper": 16.0,
        }
        empty_row = dict(full_row)
        empty_row.update(
            order_no="ORD002",
            result_no="RES002",
            sample_no="SAM002",
            name_id="NAME002",
            age=None,
            result=None,
            reference_range_lower=None,
            reference_range_upper=None,
            flag=None,
            source_file="report_002.pdf",
        )
        return pd.DataFrame([full_row, empty_row])

    def write_rows(self, df: pd.DataFrame) -> None:
        """Persists each row using the same per-row mapping that
        `ResultImporter.save_to_model` uses (`prepare_imported_result`),
        saving individually instead of via `save_to_model`/`bulk_create`.

        `Result`'s UUID primary key is generated in `UUIDAutoField.pre_save()`
        (see `django_audit_fields.fields.UUIDAutoField`), which Django's
        `bulk_create()` never calls (it writes `get_db_prep_save()` values
        directly, bypassing `pre_save()`). That makes `save_to_model`'s use
        of `bulk_create()` fail for this model on any backend; that bug is
        independent of the dataframe dtype round trip under test here.
        """
        for _, row in df.iterrows():
            unique_values = UniqueValues(
                to_str(row.get("order_no", "")),
                to_str(row.get("result_no", "")),
                to_str(row.get("sample_no", "")),
                to_str(row.get("result_status", "")),
                to_str(row.get("source_utestid", "")),
                to_str(row.get("utestid", "")),
                to_datetime(row.get("result_datetime")),
                to_str(row.get("name_id", "")),
            )
            self.importer.prepare_imported_result(unique_values, row).save()

    def test_round_trip_dtypes_and_values(self):
        df_in = self.build_source_df()

        self.write_rows(df_in)
        self.assertEqual(Result.objects.count(), 2)

        df_out = self.importer.model_to_dataframe()
        self.assertEqual(len(df_out), 2)

        for col in STRING_COLS:
            self.assertEqual(str(df_out[col].dtype), "string", col)
        for col in INT_COLS:
            self.assertEqual(str(df_out[col].dtype), "Int64", col)
        for col in DECIMAL_COLS:
            self.assertEqual(df_out[col].dtype, "float64", col)
        for col in BOOL_COLS:
            self.assertEqual(df_out[col].dtype, bool, col)
        for col in DATETIME_COLS:
            # Unit-agnostic: pandas 2/3 may resolve to "us" or "ns" precision
            # depending on version; what matters is tz-aware UTC datetime64.
            self.assertTrue(isinstance(df_out[col].dtype, pd.DatetimeTZDtype), col)
            self.assertEqual(str(df_out[col].dtype.tz), "UTC", col)

        full = df_out[df_out["result_no"] == "RES001"].iloc[0]
        self.assertEqual(full["age"], 34)
        self.assertEqual(full["subject_identifier"], "101-40990001-6")
        self.assertEqual(full["result_value"], 13.4)
        self.assertEqual(full["reference_range_lower"], 12.0)
        self.assertEqual(full["reference_range_upper"], 16.0)
        self.assertEqual(full["flag"], "H")
        self.assertEqual(
            full["order_datetime"], pd.Timestamp(2026, 1, 5, tzinfo=UTC)
        )

        empty = df_out[df_out["result_no"] == "RES002"].iloc[0]
        self.assertTrue(pd.isna(empty["age"]))
        self.assertTrue(pd.isna(empty["result_value"]))
        self.assertTrue(pd.isna(empty["reference_range_lower"]))
        self.assertTrue(pd.isna(empty["flag"]))
