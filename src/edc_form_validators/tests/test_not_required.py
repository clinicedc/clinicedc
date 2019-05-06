from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, NOT_APPLICABLE

from ..form_validator import FormValidator
from ..base_form_validator import (
    ModelFormFieldValidatorError,
    InvalidModelFormFieldValidator,
)


class TestNotRequiredFieldValidator(TestCase):
    """Test not_required_if().
    """

    def test_ignored_blank1(self):
        """Asserts field_two not required if YES.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        try:
            form_validator.not_required_if(
                YES, field="field_one", field_required="field_two"
            )
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_ignored_blank2(self):
        """Asserts field_two not required if YES so raises if field_two
        is specified.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two="blah")
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.not_required_if,
            YES,
            field="field_one",
            field_required="field_two",
        )

    def test_ignored_not_applicable(self):
        """Asserts field_two not required if YES but NOT_APPLICABLE is
        same as not required.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two=NOT_APPLICABLE)
        )
        try:
            form_validator.not_required_if(
                YES, field="field_one", field_required="field_two"
            )
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_not_required(self):
        """Asserts field_two required if not YES.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=NO))
        try:
            form_validator.not_required_if(
                YES, field="field_one", field_required="field_two"
            )
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_not_required_if_true(self):
        """Asserts field not required if condition.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=NO))
        self.assertRaises(
            forms.ValidationError,
            form_validator.not_required_if_true,
            True,
            field="field_one",
        )

        try:
            form_validator.not_required_if_true(False, field="field_one")
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_required_if_specifying_inverse(self):
        class MyFormValidator1(FormValidator):
            def clean(self):
                self.required_if(
                    YES, field="field_one", field_required="field_two", inverse=True
                )

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None)
        )
        self.assertRaises(forms.ValidationError, form_validator.clean)
        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=None, field_two="blah")
        )
        self.assertRaises(forms.ValidationError, form_validator.clean)

        class MyFormValidator2(FormValidator):
            def clean(self):
                self.required_if(
                    YES, field="field_one", field_required="field_two", inverse=False
                )

        form_validator = MyFormValidator2(
            cleaned_data=dict(field_one=YES, field_two=None)
        )
        self.assertRaises(forms.ValidationError, form_validator.clean)
        form_validator = MyFormValidator2(
            cleaned_data=dict(field_one=None, field_two="blah")
        )
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_not_required_inverse_is_true(self):
        class MyFormValidator1(FormValidator):
            def clean(self):
                self.not_required_if(
                    YES, field="field_one", field_required="field_two", inverse=True
                )

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None)
        )
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two="blah")
        )
        self.assertRaises(forms.ValidationError, form_validator.clean)

        class MyFormValidator2(FormValidator):
            def clean(self):
                self.not_required_if(
                    YES, field="field_one", field_required="field_two", inverse=False
                )

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None)
        )
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=NO, field_two="blah")
        )
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")
