from django import forms
from django.test import TestCase, tag

from ..form_validator import FormValidator


class TestOutOfRangeFieldValidator(TestCase):
    def test_out_of_range_if(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=50))
        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            1,
            10,
            field="field_one",
        )

    def test_out_of_range_if_none(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=None))
        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            1,
            10,
            field="field_one",
        )

    def test_out_of_range_if_none2(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=None))

        try:
            form_validator.out_of_range_if(1, 10, field="field_one", allow_none=True)
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raise. Got {e}")

    def test_out_of_range_if2(self):
        """Asserts 50 out of range of 0-10.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=50))
        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            0,
            10,
            field="field_one",
        )

    def test_out_of_range_if_inclusive(self):
        """Asserts 50 is not out of range of 0-50.
        Default is inclusive
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=50))
        try:
            form_validator.out_of_range_if(0, 50, field="field_one")
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raise. Got {e}")

    def test_out_of_range_if_not_inclusive(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=50))
        try:
            form_validator.out_of_range_if(0, 50, field="field_one")
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raise. Got {e}")

        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            0,
            50,
            field="field_one",
            upper_inclusive=False,
        )

        form_validator = FormValidator(cleaned_data=dict(field_one=1))
        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            1,
            50,
            field="field_one",
            lower_inclusive=False,
            upper_inclusive=False,
        )

        form_validator = FormValidator(cleaned_data=dict(field_one=0))
        self.assertRaises(
            forms.ValidationError,
            form_validator.out_of_range_if,
            1,
            50,
            field="field_one",
            lower_inclusive=False,
            upper_inclusive=False,
        )
