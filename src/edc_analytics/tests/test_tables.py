import pandas as pd
from django.test import TestCase
from edc_constants.constants import FEMALE, MALE

from edc_analytics import RowStatisticsWithGender
from edc_analytics.constants import COUNT_COLUMN, MEAN_RANGE, MEDIAN_IQR, MEDIAN_RANGE
from edc_analytics.row.row_statistics import RowStatistics


class TestTablesTestCase(TestCase):

    def setUp(self):
        self.age_values = [25, 30, 32, 87, 18, 44, 76, 57, 52, 58]
        self.gender_values = [
            MALE,
            MALE,
            FEMALE,
            MALE,
            FEMALE,
            FEMALE,
            MALE,
            FEMALE,
            FEMALE,
            FEMALE,
        ]
        self.df_all = pd.DataFrame(data={"age": self.age_values, "gender": self.gender_values})

    def test_ok(self):
        df_numerator = self.df_all[self.df_all.gender == MALE]
        df_denominator = self.df_all
        rs = RowStatistics(
            colname="age",
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
        )

        self.assertEqual(rs.as_dict().get("count"), 4)
        self.assertEqual(rs.as_dict().get("rowtotal"), 4)
        self.assertEqual(rs.as_dict().get("coltotal"), 10)
        self.assertEqual(rs.as_dict().get("colprop"), 0.4)
        self.assertEqual(rs.as_dict().get("mean"), df_numerator.age.mean())
        self.assertEqual(rs.as_dict().get("sd"), df_numerator.age.std())

        dct = {
            COUNT_COLUMN: 0,
            "coltotal": 0,
            "rowtotal": 0,
            "total": 0,
            "colprop": 0,
            "rowprop": 0,
            "mean": 0,
            "sd": 0,
            "min": 0,
            "max": 0,
            "q25": 0,
            "q50": 0,
            "q75": 0,
            "ci95l": 0,
            "ci95h": 0,
        }
        self.assertEqual(list(rs.as_dict().keys()), list(dct.keys()))

    def test_age_gte_50(self):
        df_numerator = self.df_all[
            (self.df_all.gender == MALE) & (self.df_all.age >= 50)
        ].copy()
        df_denominator = self.df_all[self.df_all.age >= 50].copy()
        rs = RowStatistics(
            colname="age",
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
        )

        self.assertEqual(rs.as_dict().get("count"), df_numerator.age.count())
        self.assertEqual(rs.as_dict().get("rowtotal"), df_numerator.age.count())
        self.assertEqual(rs.as_dict().get("coltotal"), df_denominator.age.count())
        self.assertEqual(
            rs.as_dict().get("colprop"), df_numerator.age.count() / df_denominator.age.count()
        )
        self.assertEqual(rs.as_dict().get("mean"), df_numerator.age.mean())
        self.assertEqual(rs.as_dict().get("sd"), df_numerator.age.std())

    def test_formatted_cell(self):
        df_numerator = self.df_all[
            (self.df_all.gender == MALE) & (self.df_all.age >= 50)
        ].copy()
        df_denominator = self.df_all[self.df_all.age >= 50].copy()
        rs = RowStatistics(
            colname="age",
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
        )
        self.assertEqual(rs.formatted_cell(), "2")
        rs = RowStatistics(
            colname="age",
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
            style=MEDIAN_RANGE,
            places=0,
        )
        self.assertEqual(rs.formatted_cell(), "82 (76, 87)")
        rs = RowStatistics(
            colname="age",
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
            style=MEAN_RANGE,
            places=0,
        )
        self.assertEqual(rs.formatted_cell(), "82 (76, 87)")

    def test_row(self):
        df_numerator = self.df_all[(self.df_all.age >= 50)].copy()
        df_denominator = self.df_all[(self.df_all.age >= 50)].copy()
        RowStatisticsWithGender(
            columns={
                FEMALE: (MEDIAN_IQR, 2),
                MALE: (MEDIAN_IQR, 2),
                "All": (MEAN_RANGE, 2),
            },
            df_numerator=df_numerator,
            df_denominator=df_denominator,
            df_all=self.df_all,
            colname="age",
        )
