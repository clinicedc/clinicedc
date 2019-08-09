from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO
from form_validators_app.models import TestModel

from ..form_validator import FormValidator
from ..base_form_validator import (
    ModelFormFieldValidatorError,
    InvalidModelFormFieldValidator,
)
from ..form_validator_mixin import FormValidatorMixin


class TestFieldValidator(TestCase):
    def test_form_validator(self):
        """Asserts raises if cleaned data is None; that is, not
        provided.
        """
        try:
            FormValidator(cleaned_data={})
        except ModelFormFieldValidatorError as e:
            self.fail(f"ModelFormFieldValidatorError unexpectedly raised. Got {e}")

    def test_form_validator_cleaned_data_is_none(self):
        """Asserts raises if cleaned data is None; that is, not
        provided.
        """
        self.assertRaises(
            ModelFormFieldValidatorError, FormValidator, cleaned_data=None
        )

    def test_no_responses(self):
        """Asserts raises if no response provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(InvalidModelFormFieldValidator, form_validator.required_if)

    def test_no_field(self):
        """Asserts raises if no field provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(
            InvalidModelFormFieldValidator, form_validator.required_if, YES
        )

    def test_no_field_required(self):
        """Asserts raises if "field required" not provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(
            InvalidModelFormFieldValidator,
            form_validator.required_if,
            YES,
            field="field",
        )

    def test_no_cleaned_data(self):
        self.assertRaises(
            ModelFormFieldValidatorError, FormValidator, cleaned_data=None
        )

    def test_cleaned_data_ignored(self):
        form_validator = FormValidator(cleaned_data=dict(not_this_field=1))
        try:
            form_validator.required_if(
                YES, field="field_one", field_required="field_two"
            )
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")


class TestFormValidatorInForm(TestCase):
    def test_form(self):
        class TestFormValidator(FormValidator):
            def clean(self):
                self.required_if(YES, field="f1", field_required="f2")

        class TestModelForm(FormValidatorMixin, forms.ModelForm):

            form_validator_cls = TestFormValidator

            class Meta:
                model = TestModel
                fields = "__all__"

        form = TestModelForm(data=dict(f1=NO, f2="blah"))
        self.assertFalse(form.is_valid())
        self.assertIn("f2", form._errors)
        self.assertEqual(["This field is not required."], form._errors.get("f2"))
        form = TestModelForm(data=dict(f1=YES, f2="blah"))
        self.assertNotIn("f2", form._errors or {})
