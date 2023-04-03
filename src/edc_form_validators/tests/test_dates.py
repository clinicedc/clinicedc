from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_utils import get_utcnow

from edc_form_validators.form_validator import FormValidator


class TestDateFieldValidator(TestCase):
    def test_both_given_raises(self):
        now = datetime.now().astimezone(ZoneInfo("Africa/Gaborone"))
        past = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=past, report_datetime=now))
        with self.assertRaises(TypeError) as cm:
            form_validator.date_is_past_or_raise(field="my_date", field_value=past)
        self.assertIn("Expected field name or field value but not both", str(cm.exception))

    def test_one_or_none_given_ok(self):
        form_validator = FormValidator(cleaned_data=dict(my_date=None, report_datetime=None))
        try:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")
        now = datetime.now().astimezone(ZoneInfo("Africa/Gaborone"))
        form_validator = FormValidator(cleaned_data=dict(my_date=None, report_datetime=now))
        try:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")
        form_validator = FormValidator(cleaned_data=dict(my_date=now, report_datetime=None))
        try:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_before_report_datetime_or_raise(self):
        now = get_utcnow()
        future = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=future, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_before_report_datetime_or_raise,
            field="my_date",
        )

    def test_date_is_after_report_datetime_or_raise(self):
        now = get_utcnow()
        past = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=past, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_after_report_datetime_or_raise,
            field="my_date",
        )

        future = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=future, report_datetime=now))
        try:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_future_or_raise(self):
        now = get_utcnow()
        past = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=past, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_future_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_future_or_raise(field="my_date")
        self.assertIn("Expected a future date", str(cm.exception.messages))

        future = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=future, report_datetime=now))
        try:
            form_validator.date_is_future_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_past_or_raise(self):
        now = get_utcnow()
        future = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=future, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_past_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_past_or_raise(field="my_date")
        self.assertIn("Expected a past date", str(cm.exception.messages))

        past = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=past, report_datetime=now))
        try:
            form_validator.date_is_past_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_equal_or_raise(self):
        now = get_utcnow()
        past = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=past, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_equal_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_equal_or_raise(field="my_date")
        self.assertIn("Expected dates to match", str(cm.exception.messages))
        form_validator = FormValidator(cleaned_data=dict(my_date=now, report_datetime=now))
        try:
            form_validator.date_is_equal_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_timezone(self):
        now = datetime.now().astimezone(ZoneInfo("Africa/Gaborone"))
        future = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=future, report_datetime=now))
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_past_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_past_or_raise(field="my_date")
        self.assertIn("Expected a past date", str(cm.exception.messages))
