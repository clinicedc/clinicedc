from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_utils import get_utcnow

from .models import ModelWithDateValidators, ModelWithPhoneValidators


class DateForm(forms.ModelForm):
    class Meta:
        model = ModelWithDateValidators
        fields = "__all__"


class PhoneForm(forms.ModelForm):
    class Meta:
        model = ModelWithPhoneValidators
        fields = "__all__"


class TestValidators(TestCase):
    def test_date_validators(self):

        future_datetime = get_utcnow() + relativedelta(days=10)
        form = DateForm(data={"datetime_not_future": future_datetime})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get("datetime_not_future"), ["Cannot be a future date/time"]
        )

        future_date = (get_utcnow() + relativedelta(days=10)).date()
        form = DateForm(data={"date_not_future": future_date})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get("date_not_future"), ["Cannot be a future date"]
        )

        past_datetime = get_utcnow() - relativedelta(days=10)
        form = DateForm(data={"datetime_is_future": past_datetime})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get("datetime_is_future"), ["Expected a future date/time"]
        )

        past_date = (get_utcnow() - relativedelta(days=10)).date()
        form = DateForm(data={"date_is_future": past_date})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("date_is_future"), ["Expected a future date"])

    def test_phone_validtors1(self):
        form = PhoneForm(data={"cell": "ABC", "tel": "ABC"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("cell"), ["Invalid format."])
        self.assertEqual(form.errors.get("tel"), ["Invalid format."])

        form = PhoneForm(data={"cell": "777777777", "tel": "777777777"})
        self.assertTrue(form.is_valid())

        form = PhoneForm(data={"cell": "777777777", "tel": "777777777 ext 2205"})
        self.assertTrue(form.is_valid())
