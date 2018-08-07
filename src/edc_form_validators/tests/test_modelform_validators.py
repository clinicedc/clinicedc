from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, DWTA, NOT_APPLICABLE

from ..form_validator import FormValidator
from ..base_form_validator import ModelFormFieldValidatorError, InvalidModelFormFieldValidator
from ..form_validator_mixin import FormValidatorMixin
from .models import TestModel


class TestFieldValidator(TestCase):

    def test_form_validator(self):
        """Asserts raises if cleaned data is None; that is, not
        provided.
        """
        try:
            FormValidator(cleaned_data={})
        except ModelFormFieldValidatorError as e:
            self.fail(
                f'ModelFormFieldValidatorError unexpectedly raised. Got {e}')

    def test_form_validator_cleaned_data_is_none(self):
        """Asserts raises if cleaned data is None; that is, not
        provided.
        """
        self.assertRaises(
            ModelFormFieldValidatorError, FormValidator, cleaned_data=None)

    def test_no_responses(self):
        """Asserts raises if no response provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(
            InvalidModelFormFieldValidator,
            form_validator.required_if)

    def test_no_field(self):
        """Asserts raises if no field provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(
            InvalidModelFormFieldValidator,
            form_validator.required_if, YES)

    def test_no_field_required(self):
        """Asserts raises if no field required provided.
        """
        form_validator = FormValidator(cleaned_data={})
        self.assertRaises(
            InvalidModelFormFieldValidator,
            form_validator.required_if, YES, field='field')


class TestRequiredFieldValidator1(TestCase):
    """Test required_if().
    """

    def test_ignored(self):
        form_validator = FormValidator(cleaned_data=dict(not_this_field=1))
        try:
            form_validator.required_if(
                YES, field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')

    def test_raises_for_missing_field_required_value(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            YES, field='field_one', field_required='field_two')

    def test_required_values_provided_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two='something'))
        try:
            form_validator.required_if(
                YES, field='field_one', field_required='field_two')
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')

    def test_not_required_but_field_value_provided_raises(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two='something'))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if,
            YES, field='field_one', field_required='field_two')

    def test_required_field_value_not_applicable_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two=NOT_APPLICABLE))
        try:
            form_validator.required_if(
                YES, DWTA, field='field_one', field_required='field_two')
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')

    def test_required_field_value_dwta_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=DWTA))
        try:
            form_validator.required_if(
                YES, DWTA, field='field_one', field_required='field_two',
                optional_if_dwta=True)
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')


class TestRequiredFieldValidator2(TestCase):
    """Test not_required_if().
    """

    def test_ignored_blank1(self):
        """Asserts field_two not required if YES.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        try:
            form_validator.not_required_if(
                YES, field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')

    def test_ignored_blank2(self):
        """Asserts field_two not required if YES so raises if field_two
        is specified.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two='blah'))
        self.assertRaises(
            forms.ValidationError,
            form_validator.not_required_if,
            YES, field='field_one', field_required='field_two')

    def test_ignored_not_applicable(self):
        """Asserts field_two not required if YES but NOT_APPLICABLE is
        same as not required.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two=NOT_APPLICABLE))
        try:
            form_validator.not_required_if(
                YES, field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')

    def test_not_required(self):
        """Asserts field_two required if not YES.
        """
        form_validator = FormValidator(cleaned_data=dict(field_one=NO))
        try:
            form_validator.not_required_if(
                YES, field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')

    def test_required_if_specifying_inverse(self):

        class MyFormValidator1(FormValidator):
            def clean(self):
                self.required_if(
                    YES, field='field_one', field_required='field_two',
                    inverse=True)
        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None))
        self.assertRaises(forms.ValidationError, form_validator.clean)
        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=None, field_two='blah'))
        self.assertRaises(forms.ValidationError, form_validator.clean)

        class MyFormValidator2(FormValidator):
            def clean(self):
                self.required_if(
                    YES, field='field_one', field_required='field_two',
                    inverse=False)
        form_validator = MyFormValidator2(
            cleaned_data=dict(field_one=YES, field_two=None))
        self.assertRaises(forms.ValidationError, form_validator.clean)
        form_validator = MyFormValidator2(
            cleaned_data=dict(field_one=None, field_two='blah'))
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail('ValidationError unexpectedly raised')

    def test_not_required_inverse_is_true(self):
        class MyFormValidator1(FormValidator):
            def clean(self):
                self.not_required_if(
                    YES, field='field_one', field_required='field_two',
                    inverse=True)
        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None))
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail('ValidationError unexpectedly raised')

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two='blah'))
        self.assertRaises(forms.ValidationError, form_validator.clean)

        class MyFormValidator2(FormValidator):
            def clean(self):
                self.not_required_if(
                    YES, field='field_one', field_required='field_two',
                    inverse=False)
        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=YES, field_two=None))
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail('ValidationError unexpectedly raised')

        form_validator = MyFormValidator1(
            cleaned_data=dict(field_one=NO, field_two='blah'))
        try:
            form_validator.clean()
        except forms.ValidationError:
            self.fail('ValidationError unexpectedly raised')


class TestApplicableFieldValidator(TestCase):
    """Test applicable_if().
    """

    def test_applicable_if(self):
        """Asserts field_two applicable if YES.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=YES, field_two=NOT_APPLICABLE))
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if,
            YES, field='field_one', field_applicable='field_two')

    def test_applicable_if_true(self):
        """Asserts field_two applicable if test_con1 and test_con2
        are YES.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=('test_con1' == YES
                                         and 'test_con2' == YES),
                              field_two=NOT_APPLICABLE))
        self.assertRaises(
            forms.ValidationError,
            form_validator.applicable_if_true,
            condition='field_one', field_applicable='field_two')

    def test_not_applicable_only_if(self):
        """Asserts field_two is not applicable if test_con1 is No.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two=10))
        self.assertRaises(
            forms.ValidationError,
            form_validator.not_applicable_only_if,
            NO,
            field='field_one', field_applicable='field_two')

    def test_not_applicable_only_if2(self):
        """Asserts field_two is not applicable if test_con1 is No.
        """
        form_validator = FormValidator(
            cleaned_data=dict(field_one=NO, field_two=None))
        try:
            form_validator.not_required_if(
                NO, field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')


class TestFormValidatorInForm(TestCase):

    def test_form(self):

        class TestFormValidator(FormValidator):

            def clean(self):
                self.required_if(
                    YES,
                    field='f1',
                    field_required='f2')

        class TestModelForm(FormValidatorMixin, forms.ModelForm):

            form_validator_cls = TestFormValidator

            class Meta:
                model = TestModel
                fields = '__all__'

        form = TestModelForm(data=dict(f1=NO, f2='blah'))
        self.assertFalse(form.is_valid())
        self.assertIn('f2', form._errors)
        self.assertEqual(['This field is not required.'],
                         form._errors.get('f2'))
        form = TestModelForm(data=dict(f1=YES, f2='blah'))
        self.assertNotIn('f2', form._errors or {})


class TestRequiredIfNotNoneFieldValidator(TestCase):
    """Test required_if_not_none().
    """

    def test_ignored(self):
        form_validator = FormValidator(cleaned_data=dict(not_this_field=1))
        try:
            form_validator.required_if_not_none(
                field='field_one', field_required='field_two')
        except (ModelFormFieldValidatorError, InvalidModelFormFieldValidator) as e:
            self.fail(f'Exception unexpectedly raised. Got {e}')

    def test_raises_for_missing_field_required_value(self):
        form_validator = FormValidator(cleaned_data=dict(field_one=YES))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if_not_none,
            field='field_one', field_required='field_two')

    def test_required_values_provided_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one='nothing', field_two='something'))
        try:
            form_validator.required_if_not_none(
                field='field_one', field_required='field_two')
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')

    def test_not_required_but_field_value_provided_raises(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=None, field_two='something'))
        self.assertRaises(
            forms.ValidationError,
            form_validator.required_if_not_none,
            field='field_one', field_required='field_two')

    def test_required_field_value_not_applicable_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=None, field_two=NOT_APPLICABLE))
        try:
            form_validator.required_if_not_none(
                field='field_one', field_required='field_two')
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')

    def test_required_field_value_dwta_ok(self):
        form_validator = FormValidator(
            cleaned_data=dict(field_one=DWTA))
        try:
            form_validator.required_if_not_none(
                field='field_one', field_required='field_two',
                optional_if_dwta=True)
        except forms.ValidationError as e:
            self.fail(f'forms.ValidationError unexpectedly raised. Got {e}')
