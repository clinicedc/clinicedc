from django import forms
from django.test import TestCase
from edc_constants.constants import NO, NOT_APPLICABLE, YES

from ..base_form_validator import (
    InvalidModelFormFieldValidator,
    ModelFormFieldValidatorError,
)
from ..form_validator import FormValidator


class TestApplicableFieldValidator(TestCase):
    """Test applicable_if()."""

    def test_applicable_if(self):
        """Asserts field_two applicable if YES."""
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two=NOT_APPLICABLE)
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if,
            YES,
            field="field_one",
            field_applicable="field_two",
        )

        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two=NOT_APPLICABLE)
        )
        try:
            form_validator.applicable_if(NO, field="field_one", field_applicable="field_two")
        except forms.ValidationError as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")
        else:
            pass

        form_validator = FormValidator(cleaned_data=dict(field_one=YES, field_two=None))
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if,
            NO,
            field="field_one",
            field_applicable="field_two",
        )

        form_validator = FormValidator(cleaned_data=dict(field_one=YES, field_two=None))
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if,
            YES,
            field="field_one",
            field_applicable="field_two",
        )

    def test_applicable_if_true(self):
        """Asserts field_two applicable if test_con1 and test_con2
        are YES.
        """
        form_validator = FormValidator(
            cleaned_data=dict(
                field_one=("test_con1" == YES and "test_con2" == YES),
                field_two=NOT_APPLICABLE,
            )
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if_true,
            condition="field_one",
            field_applicable="field_two",
        )

    def test_not_applicable_only_if(self):
        """Asserts field_two is not applicable if test_con1 is No."""
        form_validator = FormValidator(cleaned_data=dict(field_one=NO, field_two=10))
        self.assertRaises(
            forms.ValidationError,
            form_validator.not_applicable_only_if,
            NO,
            field="field_one",
            field_applicable="field_two",
        )

    def test_not_applicable_only_if2(self):
        """Asserts field_two is not applicable if test_con1 is No."""
        form_validator = FormValidator(cleaned_data=dict(field_one=NO, field_two=None))
        try:
            form_validator.not_required_if(NO, field="field_one", field_required="field_two")
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")
