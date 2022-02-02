from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_utils import get_utcnow

from ..models import (
    ModelWithDateValidators,
    ModelWithDHDurationValidators,
    ModelWithPhoneValidators,
)


class DateForm(forms.ModelForm):
    class Meta:
        model = ModelWithDateValidators
        fields = "__all__"


class DHDurationForm(forms.ModelForm):
    class Meta:
        model = ModelWithDHDurationValidators
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
        self.assertEqual(form.errors.get("date_not_future"), ["Cannot be a future date"])

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

    def test_phone_validators1(self):
        form = PhoneForm(data={"cell": "ABC", "tel": "ABC"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("cell"), ["Invalid format."])
        self.assertEqual(form.errors.get("tel"), ["Invalid format."])

        form = PhoneForm(data={"cell": "777777777", "tel": "777777777"})
        self.assertTrue(form.is_valid())

        form = PhoneForm(data={"cell": "777777777", "tel": "777777777 ext 2205"})
        self.assertTrue(form.is_valid())


class TestFieldValidators(TestCase):
    def test_dh_duration_field_validator_allows_expected_dh_matches(self):
        matching_strings = [
            "0d0h",
            "00d00h",
            "000d00h",
            "0d",
            "0h",
            "0d1h",
            "1d0h",
            "3d",
            "10d",
            "10d0h",
            "10d9h",
            "10d10h",
            "11d",
            "99d",
            "100d",
            "100d0h",
            "100d9h",
            "100d23h",
            "101d",
            "999d",
            "4h",
            "04h",
            "10h",
            "11h",
            "19h",
            "20h",
            "21h",
            "22h",
            "23h",
        ]
        for string in matching_strings:
            with self.subTest(string=string):
                form = DHDurationForm(data={"duration_dh": string})
                self.assertTrue(
                    form.is_valid(),
                    f"Expected DurationDHField to validate string '{string}' "
                    f"without errors.  Got {form.errors.as_data()}",
                )

    def test_dh_duration_field_validator_flags_dh_mismatches(self):
        mismatching_strings = [
            "0000d",
            "1000d",
            "000h",
            "24h",
            "1d24h",
            "25h",
            "119h",
            "225h",
            "5",
            "15",
            "12345",
            "d",
            "h",
            "x",
            "dh",
            "5 d",
            "5d.",
            "3 h",
            "5d 3h",
            "5d7",
            "5d10",
            "5d20",
            "5d24h",
            "5d25h",
        ]
        for string in mismatching_strings:
            with self.subTest(string=string):
                form = DHDurationForm(data={"duration_dh": string})
                self.assertFalse(
                    form.is_valid(),
                    f"Expected DurationDHField to flag error for string '{string}'. "
                    f"Got {form.errors.as_data()}",
                )
                self.assertDictEqual(
                    form.errors,
                    {
                        "duration_dh": (
                            [
                                "Invalid format. Expected combinations of days and hours "
                                "(dh): Something like 3d2h, 7d, 12h, etc. No spaces allowed."
                            ]
                        )
                    },
                )

    def test_dh_duration_field_validator_flags_if_gt_7_chars(self):
        expected_mismatches = [
            "12345678",
            "123456789",
            "0000d00h",
            "000d000h",
            "0000d0000h",
        ]
        for string in expected_mismatches:
            with self.subTest(string=string):
                form = DHDurationForm(data={"duration_dh": string})
                self.assertFalse(
                    form.is_valid(),
                    f"Expected DurationDHField to flag max_length error for string '{string}' "
                    f"(len {len(string)}). Got {form.errors.as_data()}",
                )
                self.assertDictEqual(
                    form.errors,
                    {
                        "duration_dh": (
                            [
                                "Ensure this value has at most 7 characters "
                                f"(it has {len(string)})."
                            ]
                        )
                    },
                )
