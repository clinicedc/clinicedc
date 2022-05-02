from copy import copy
from typing import Any, Union

from django.core.exceptions import NON_FIELD_ERRORS
from django.db.models import Model
from django.forms import ValidationError, forms

APPLICABLE_ERROR = "applicable"
INVALID_ERROR = "invalid"
NOT_APPLICABLE_ERROR = "not_applicable"
NOT_REQUIRED_ERROR = "not_required"
REQUIRED_ERROR = "required"
OUT_OF_RANGE_ERROR = "out_of_range"


class InvalidModelFormFieldValidator(Exception):
    def __init__(self, message, code=None):
        message = f"Invalid field validator. Got '{message}'"
        super().__init__(message)
        self.code = code


class ModelFormFieldValidatorError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class BaseFormValidator:

    default_fk_stored_field_name = "name"
    default_fk_display_field_name = "display_name"

    def __init__(
        self, cleaned_data: dict = None, instance: Model = None, data: dict = None
    ) -> None:
        self._errors: dict = {}
        self._error_codes: list = []
        self.cleaned_data = copy(cleaned_data)
        self.data = copy(data)
        self.instance = instance
        self.original_cleaned_data = copy(cleaned_data)
        if cleaned_data is None:
            raise ModelFormFieldValidatorError(
                f"{repr(self)}. Expected a cleaned_data dictionary. Got None."
            )
        try:
            self.instance.id
        except AttributeError:
            self.add_form = True
            self.change_form = False
        else:
            self.add_form = False
            self.change_form = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(cleaned_data={self.cleaned_data})"

    def __str__(self) -> str:
        return str(self.cleaned_data)

    def clean(self) -> None:
        """Override with logic normally in ModelForm.clean()"""
        pass

    def _clean(self) -> None:
        self.clean()

    def update_cleaned_data_from_instance(self, field: str) -> None:
        if field in self.original_cleaned_data:
            raise ModelFormFieldValidatorError(
                f"May not get form field value from instance. "
                f"This field is already in cleaned data. "
                f"Got {field}."
            )
        self.cleaned_data.update({field: getattr(self.instance, field)})

    def get(self, field: str, inline_set=None) -> Any:
        """Returns the field`s value"""
        if inline_set:
            field_value = self.get_inline_field_value(field, inline_set)
        else:
            try:
                field_value = self.cleaned_data.get(field).name
            except AttributeError:
                field_value = self.cleaned_data.get(field)
        return field_value

    def raise_validation_error(self, message: Union[dict, str], error_code: str) -> None:
        if isinstance(message, str):
            message = {NON_FIELD_ERRORS: message}
        self._errors.update(message)
        self._error_codes.append(error_code)
        raise ValidationError(message, code=error_code or INVALID_ERROR)

    def validate(self) -> dict:
        """Call in ModelForm.clean.

        For example:

            form_validator_cls = None

            def clean(self):
                cleaned_data = super().clean()
                form_validator = self.form_validator_cls(
                    cleaned_data=cleaned_data)
                cleaned_data = form_validator.validate()
                return cleaned_data

        """
        try:
            self._clean()
        except forms.ValidationError as e:
            self.capture_error_message(e)
            self.capture_error_code(e)
            raise forms.ValidationError(e)
        return self.cleaned_data

    def capture_error_message(self, e: forms.ValidationError) -> None:
        try:
            self._errors.update(**e.error_dict)
        except AttributeError:
            try:
                self._errors.update({NON_FIELD_ERRORS: e.error_list})
            except AttributeError:
                self._errors.update({NON_FIELD_ERRORS: str(e)})

    def capture_error_code(self, e: forms.ValidationError) -> None:
        try:
            self._error_codes.append(e.code)
        except AttributeError:
            pass

    def get_inline_field_value(self, field=None, inline_set=None):
        """Returns the value of the first inline field that has a value."""
        field_values = []
        total_forms = int(self.data.get(f"{inline_set}-TOTAL_FORMS"))
        for i in range(0, total_forms):
            if self.data.get(f"{inline_set}-{i}-DELETE") == "on":
                pass
            else:
                inline_field = f"{inline_set}-{i}-{field}"
                try:
                    field_values.append(self.data[inline_field])
                except KeyError:
                    break
        field_value = None
        for value in field_values:
            try:
                field_value = value.name
            except AttributeError:
                field_value = value
            if field_value:
                break
        return field_value
