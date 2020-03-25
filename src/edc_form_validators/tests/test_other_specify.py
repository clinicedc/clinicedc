from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, NOT_APPLICABLE, OTHER

from ..form_validator import FormValidator
from ..base_form_validator import (
    ModelFormFieldValidatorError,
    InvalidModelFormFieldValidator,
)
from form_validators_app.models import Alphabet


class TestApplicableFieldValidator(TestCase):
    """Test applicable_if().
    """

    def test_other_specify(self):
        form_validator = FormValidator(cleaned_data=dict(f5=OTHER))
        self.assertRaises(
            forms.ValidationError, form_validator.validate_other_specify, field="f5"
        )

    def test_other_specify2(self):
        form_validator = FormValidator(cleaned_data=dict(f5="HELLO"))
        try:
            form_validator.validate_other_specify(field="f5")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_other_specify3(self):
        form_validator = FormValidator(cleaned_data=dict(f5=OTHER, f5_other="blah"))
        try:
            form_validator.validate_other_specify(field="f5")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_other_specify4(self):
        form_validator = FormValidator(cleaned_data=dict(f5=OTHER, f5_other="blah"))
        self.assertRaises(
            forms.ValidationError,
            form_validator.validate_other_specify,
            field="f5",
            other_specify_field="f2",
        )

        form_validator = FormValidator(cleaned_data=dict(f5="hello", f5_other="blah"))
        self.assertRaises(
            forms.ValidationError, form_validator.validate_other_specify, field="f5"
        )

        form_validator = FormValidator(cleaned_data=dict(f5=None, f5_other="blah"))
        self.assertRaises(
            forms.ValidationError, form_validator.validate_other_specify, field="f5"
        )

        form_validator = FormValidator(cleaned_data=dict(f5=OTHER, f2="blah"))
        try:
            form_validator.validate_other_specify(field="f5", other_specify_field="f2")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")
