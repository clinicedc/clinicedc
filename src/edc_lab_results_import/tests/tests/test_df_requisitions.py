from __future__ import annotations

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pandas as pd
from django.test import SimpleTestCase, tag

from edc_lab_results_import.result_importer.result_importer import ResultImporter

MODULE = "edc_lab_results_import.result_importer.result_importer"
DRAWN = pd.Timestamp(datetime(2025, 3, 1, 8, 0, tzinfo=ZoneInfo("UTC")))


def make_importer(df_utestid: pd.DataFrame) -> ResultImporter:
    """Builds a `ResultImporter` without `__init__`, which wants a real
    PDF folder and laboratory mapping files. See
    `test_result_importer_roundtrip`.
    """
    importer = ResultImporter.__new__(ResultImporter)
    importer._df_requisitions = pd.DataFrame()
    importer._df_utestid = df_utestid
    return importer


def make_df_utestid(records: list[tuple[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(records, columns=["utestid", "panel_name"]).astype("string")


def make_requisition_df() -> pd.DataFrame:
    """Shaped like `get_requisition_df`, a row per requisition and
    utest id, with its own `utestid` column.
    """
    rows = [
        ("req-fbc", "fbc", "haemoglobin"),
        ("req-fbc", "fbc", "platelets"),
        ("req-chem", "chemistry", "creatinine"),
        ("req-chem", "chemistry", "urea"),
    ]
    return pd.DataFrame(
        {
            "requisition": [r[0] for r in rows],
            "subject_identifier": ["101-00000001-1"] * len(rows),
            "visit_code": [1000.0] * len(rows),
            "visit_code_sequence": [0] * len(rows),
            "drawn_datetime": [DRAWN] * len(rows),
            "panel_name": [r[1] for r in rows],
            "utestid": [r[2] for r in rows],
        }
    ).astype({"requisition": "string", "panel_name": "string", "utestid": "string"})


@tag("lab_results_import")
@patch(f"{MODULE}.get_requisition_panel_name_map", return_value={"wbc_diff": "fbc"})
@patch(f"{MODULE}.get_requisition_df", side_effect=make_requisition_df)
class TestDfRequisitions(SimpleTestCase):
    """`get_requisition_df` already has a `utestid` column. Merging
    `df_utestid` onto it without dropping that column leaves
    `utestid_x` and `utestid_y`, and no `utestid`.
    """

    def get_df(self) -> pd.DataFrame:
        importer = make_importer(
            make_df_utestid(
                [
                    ("haemoglobin", "fbc"),
                    ("platelets", "fbc"),
                    ("neutrophil_diff", "wbc_diff"),
                    ("creatinine", "chemistry"),
                ]
            )
        )
        return importer.df_requisitions

    def test_has_one_utestid_column(self, *mocks):  # noqa: ARG002
        df = self.get_df()
        self.assertIn("utestid", df.columns)
        self.assertNotIn("utestid_x", df.columns)
        self.assertNotIn("utestid_y", df.columns)

    def test_utestids_come_from_df_utestid(self, *mocks):  # noqa: ARG002
        """`urea` is in the requisition frame but not in `df_utestid`,
        and the wbc_diff utest id is drawn on the FBC requisition.
        """
        df = self.get_df()
        self.assertEqual(
            sorted(df.loc[df["requisition"] == "req-fbc", "utestid"].tolist()),
            ["haemoglobin", "neutrophil_diff", "platelets"],
        )
        self.assertEqual(
            df.loc[df["requisition"] == "req-chem", "utestid"].tolist(), ["creatinine"]
        )

    def test_one_row_per_requisition_and_utestid(self, *mocks):  # noqa: ARG002
        df = self.get_df()
        self.assertFalse(df.duplicated(subset=["requisition", "utestid"]).any())
        self.assertEqual(len(df), 4)
