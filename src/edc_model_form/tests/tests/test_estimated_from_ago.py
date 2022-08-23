from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import TestCase

from edc_model_form.mixins import EstimatedDateFromAgoFormMixin


class TestEstimatedFromAgo(TestCase):
    def test_years_ago(self):
        class MyFormValidator(EstimatedDateFromAgoFormMixin):
            cleaned_data = {}

        cleaned_data = {
            "report_datetime": datetime(2000, 5, 1).astimezone(ZoneInfo("UTC")),
            "ago_field": "5y",
        }
        expected_date = (datetime(1995, 5, 1).astimezone(ZoneInfo("UTC"))).date()

        form_validator = MyFormValidator()
        form_validator.cleaned_data = cleaned_data
        self.assertEqual(expected_date, form_validator.estimated_date_from_ago("ago_field"))

    def test_years_days_ago(self):
        class MyFormValidator(EstimatedDateFromAgoFormMixin):
            cleaned_data = {}

        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10).astimezone(ZoneInfo("UTC")),
            "ago_field": "5y3m",
        }
        expected_date = (datetime(1995, 2, 10).astimezone(ZoneInfo("UTC"))).date()

        form_validator = MyFormValidator()
        form_validator.cleaned_data = cleaned_data
        self.assertEqual(expected_date, form_validator.estimated_date_from_ago("ago_field"))

    def test_with_years_and_days_raises(self):
        class MyFormValidator(EstimatedDateFromAgoFormMixin):
            cleaned_data = {}

        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10).astimezone(ZoneInfo("UTC")),
            "ago_field": "5y3d",
        }

        form_validator = MyFormValidator()
        form_validator.cleaned_data = cleaned_data
        self.assertRaises(ValidationError, form_validator.estimated_date_from_ago, "ago_field")

    def test_with_days_ago(self):
        class MyFormValidator(EstimatedDateFromAgoFormMixin):
            cleaned_data = {}

        cleaned_data = {
            "report_datetime": datetime(2000, 5, 10).astimezone(ZoneInfo("UTC")),
            "ago_field": "3d",
        }
        expected_date = (datetime(2000, 5, 7).astimezone(ZoneInfo("UTC"))).date()

        form_validator = MyFormValidator()
        form_validator.cleaned_data = cleaned_data
        self.assertEqual(expected_date, form_validator.estimated_date_from_ago("ago_field"))
