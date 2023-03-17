from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_model import estimated_date_from_ago


class TestEstimatedFromAgo(TestCase):
    def test_years_ago(self):
        cleaned_data = {
            "report_datetime": datetime(2000, 5, 1, tzinfo=ZoneInfo("UTC")),
            "ago_field": "5y",
        }
        expected_date = (datetime(1995, 5, 1, tzinfo=ZoneInfo("UTC"))).date()

        self.assertEqual(
            expected_date,
            estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
        )

    def test_years_days_ago(self):
        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10, tzinfo=ZoneInfo("UTC")),
            "ago_field": "5y3m",
        }
        expected_date = (datetime(1995, 2, 10, tzinfo=ZoneInfo("UTC"))).date()

        self.assertEqual(
            expected_date,
            estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
        )

        cleaned_data = {
            "report_datetime": datetime(2000, 5, 31, tzinfo=ZoneInfo("UTC")),
            "ago_field": "5y3m",
        }
        expected_date = (datetime(1995, 2, 28, tzinfo=ZoneInfo("UTC"))).date()

        self.assertEqual(
            expected_date,
            estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
        )

        for i in range(4, 9):
            cleaned_data = {
                "report_datetime": datetime(2000, i, 10, tzinfo=ZoneInfo("UTC")),
                "ago_field": "5y3m",
            }
            expected_date = (datetime(1995, i - 3, 10, tzinfo=ZoneInfo("UTC"))).date()

            self.assertEqual(
                expected_date,
                estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
            )

        for i in range(1, 3):
            cleaned_data = {
                "report_datetime": datetime(2000, i + 3, 10, tzinfo=ZoneInfo("UTC")),
                "ago_field": "5y3m",
            }
            expected_date = (datetime(1995, i, 10, tzinfo=ZoneInfo("UTC"))).date()

            self.assertEqual(
                expected_date,
                estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
            )

    def test_with_years_and_days_raises(self):
        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10, tzinfo=ZoneInfo("UTC")),
            "ago_field": "5y3d",
        }

        self.assertRaises(
            ValidationError,
            estimated_date_from_ago,
            cleaned_data=cleaned_data,
            ago_field="ago_field",
        )

    def test_with_days_ago(self):
        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10, tzinfo=ZoneInfo("UTC")),
            "ago_field": "3d",
        }
        expected_date = (datetime(2000, 5, 7, tzinfo=ZoneInfo("UTC"))).date()

        self.assertEqual(
            expected_date,
            estimated_date_from_ago(cleaned_data=cleaned_data, ago_field="ago_field"),
        )
