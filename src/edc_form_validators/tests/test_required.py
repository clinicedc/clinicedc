from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, DWTA, NOT_APPLICABLE

from ..form_validator import FormValidator


class TestRequiredFieldValidator(TestCase):
    """Test required_if and required_if_not_none.
    """

    def test_required_if_raises_for_field_required_is_none(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            YES,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_ok_required_zero(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=0))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            0,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_ok_required_value_none(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=None))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            None,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_raises_on_value_not_required(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two="something")
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            YES,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_ok_not_applicable(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two=NOT_APPLICABLE)
        )
        try:
            form_validator.required_if(
                YES, DWTA, field="field_one", field_required="field_two"
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")

    def test_required_if_ok_dwta(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=DWTA))
        try:
            form_validator.required_if(
                YES,
                DWTA,
                field="field_one",
                field_required="field_two",
                optional_if_dwta=True,
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")

    def test_required_if_not_none_raises_for_missing_field_required_value(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if_not_none,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_not_none_required_values_provided_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one="nothing", field_two="something")
        )
        try:
            form_validator.required_if_not_none(
                field="field_one", field_required="field_two"
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")

    def test_required_if_not_none_not_required_but_field_value_provided_raises(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=None, field_two="something")
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if_not_none,
            field="field_one",
            field_required="field_two",
        )

    def test_required_if_not_none_required_field_value_not_applicable_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=None, field_two=NOT_APPLICABLE)
        )
        try:
            form_validator.required_if_not_none(
                field="field_one", field_required="field_two"
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")

    def test_required_if_not_none_required_field_value_dwta_ok(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=DWTA))
        try:
            form_validator.required_if_not_none(
                field="field_one", field_required="field_two", optional_if_dwta=True
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")
