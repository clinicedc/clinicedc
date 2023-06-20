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
            form_validator.date_is_before_or_raise(field="my_date", field_value=past)
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
        not_before = now + relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_before, report_datetime=now)
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_before_report_datetime_or_raise,
            field="my_date",
        )

    def test_date_is_after_report_datetime_or_raise(self):
        now = get_utcnow()
        after = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=after, report_datetime=now))
        try:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        not_after = now - relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_after, report_datetime=now)
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_after_report_datetime_or_raise(field="my_date")
        self.assertIn("my_date", cm.exception.error_dict)
        self.assertIn(
            "Invalid. Expected a date after",
            str(cm.exception.error_dict.get("my_date")),
        )

    def test_date_is_after_or_raise(self):
        now = get_utcnow()
        not_after = now - relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_after, report_datetime=now)
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_after_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_after_or_raise(field="my_date")
        self.assertIn("Expected a date after", str(cm.exception.messages))

        after = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=after, report_datetime=now))
        try:
            form_validator.date_is_after_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_on_or_after_or_raise(self):
        now = get_utcnow()
        not_after = now - relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_after, report_datetime=now)
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_after_or_raise(
                field="my_date",
                inclusive=True,
            )
        self.assertIn("Expected a date on or after", str(cm.exception.messages))

        on = now + relativedelta(minutes=10)
        form_validator = FormValidator(cleaned_data=dict(my_date=on, report_datetime=now))
        try:
            form_validator.date_is_after_or_raise(
                field="my_date",
                inclusive=True,
            )
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        after = now + relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=after, report_datetime=now))
        try:
            form_validator.date_is_after_or_raise(
                field="my_date",
                inclusive=True,
            )
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_date_is_before_or_raise(self):
        now = get_utcnow()
        before = now - relativedelta(days=1)
        form_validator = FormValidator(cleaned_data=dict(my_date=before, report_datetime=now))
        try:
            form_validator.date_is_before_or_raise(field="my_date")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        not_before = now + relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_before, report_datetime=now)
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_before_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_before_or_raise(field="my_date")
        self.assertIn("Expected a date before", str(cm.exception.messages))

    def test_date_is_equal_or_raise(self):
        now = get_utcnow()
        not_equal = now - relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_equal, report_datetime=now)
        )
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
        not_before = now + relativedelta(days=1)
        form_validator = FormValidator(
            cleaned_data=dict(my_date=not_before, report_datetime=now)
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.date_is_before_or_raise,
            field="my_date",
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.date_is_before_or_raise(field="my_date")
        self.assertIn("Expected a date before ", str(cm.exception.messages))
