from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_utils import get_utcnow

from ..form_validator import FormValidator


class TestDateFieldValidator(TestCase):
    def test_date_is_before_report_datetime(self):
        now = get_utcnow()
        before = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=before, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.invalid_if_before_report_datetime,
            field="my_date",
        )

    def test_date_is_after_report_datetime(self):
        now = get_utcnow()
        before = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=before, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.invalid_if_after_report_datetime,
            field="my_date",
        )
