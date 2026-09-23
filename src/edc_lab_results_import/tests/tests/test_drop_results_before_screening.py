from __future__ import annotations

from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

import pandas as pd
from django.test import TestCase, tag

from edc_lab_results_import.result_importer.result_importer import ResultImporter

UTC = ZoneInfo("UTC")
FIRST_SCREENING = datetime(2025, 3, 1, 8, 0, tzinfo=UTC)


def make_importer(df: pd.DataFrame, df_screening: pd.DataFrame) -> ResultImporter:
    """Builds a `ResultImporter` without `__init__`, which wants a real
    PDF folder and laboratory mapping files. See
    `test_result_importer_roundtrip`.
    """
    importer = ResultImporter.__new__(ResultImporter)
    importer.stdout = StringIO()
    importer.df = df
    importer._df_screening = df_screening
    return importer


def make_df_screening(*screening_datetimes: datetime) -> pd.DataFrame:
    """Shaped like `df_screening`, datetimes as read_frame returns them."""
    return pd.DataFrame(
        {
            "screening_identifier": [f"S{i}" for i in range(len(screening_datetimes))],
            "screening_datetime": list(screening_datetimes),
            "site": ["10"] * len(screening_datetimes),
        }
    )


def make_df(*result_datetimes: datetime | None) -> pd.DataFrame:
    """Shaped like `parse_folder` output, an object column of aware
    datetimes with None where a report has no result datetime.
    """
    return pd.DataFrame(
        {
            "result_no": [str(i) for i in range(len(result_datetimes))],
            "result_datetime": pd.Series(list(result_datetimes), dtype="object"),
        }
    )


@tag("lab_results_import")
class TestDropResultsBeforeScreening(TestCase):
    def test_drops_results_before_first_screening(self):
        importer = make_importer(
            make_df(
                datetime(2025, 2, 28, 8, 0, tzinfo=UTC),
                FIRST_SCREENING,
                datetime(2025, 3, 2, 8, 0, tzinfo=UTC),
            ),
            make_df_screening(datetime(2025, 3, 5, 8, 0, tzinfo=UTC), FIRST_SCREENING),
        )
        importer.drop_results_before_screening()
        self.assertEqual(importer.df["result_no"].tolist(), ["1", "2"])
        self.assertEqual(importer.df.index.tolist(), [0, 1])

    def test_keeps_results_without_result_datetime(self):
        importer = make_importer(
            make_df(None, datetime(2025, 2, 28, 8, 0, tzinfo=UTC), FIRST_SCREENING),
            make_df_screening(FIRST_SCREENING),
        )
        importer.drop_results_before_screening()
        self.assertEqual(importer.df["result_no"].tolist(), ["0", "2"])

    def test_compares_across_timezones(self):
        """08:00 UTC is 11:00 in Dar es Salaam."""
        eat = ZoneInfo("Africa/Dar_es_Salaam")
        importer = make_importer(
            make_df(
                datetime(2025, 3, 1, 10, 59, tzinfo=eat),
                datetime(2025, 3, 1, 11, 0, tzinfo=eat),
            ),
            make_df_screening(FIRST_SCREENING),
        )
        importer.drop_results_before_screening()
        self.assertEqual(importer.df["result_no"].tolist(), ["1"])

    def test_nothing_dropped_if_no_screening(self):
        """An empty frame is not cached, so `df_screening` queries the
        screening model, which has no rows.
        """
        df = make_df(datetime(2025, 2, 28, 8, 0, tzinfo=UTC))
        importer = make_importer(df, pd.DataFrame())
        importer.drop_results_before_screening()
        self.assertEqual(importer.df["result_no"].tolist(), ["0"])

    def test_empty_df(self):
        importer = make_importer(pd.DataFrame(), make_df_screening(FIRST_SCREENING))
        importer.drop_results_before_screening()
        self.assertTrue(importer.df.empty)
