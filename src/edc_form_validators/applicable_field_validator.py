from edc_constants.constants import NOT_APPLICABLE

from .base_form_validator import BaseFormValidator
from .base_form_validator import APPLICABLE_ERROR, NOT_APPLICABLE_ERROR

"""
        instance_fields = instance_fields or []
        cleaned_data = copy(self.cleaned_data)
        for k in instance_fields:
            if k not in cleaned_data:
                cleaned_data.update({k: getattr(self.instance, k)})
        if field not in cleaned_data or field_applicable not in cleaned_data:
            raise
"""


class ApplicableFieldValidator(BaseFormValidator):
    def raise_applicable(self, field, msg=None):
        message = {field: f"This field is applicable. {msg or ''}".strip()}
        self.raise_validation_error(message, APPLICABLE_ERROR)

    def raise_not_applicable(self, field, msg=None):
        message = {field: f"This field is not applicable. {msg or ''}".strip()}
        self.raise_validation_error(message, NOT_APPLICABLE_ERROR)

    def applicable_if(
        self,
        *responses,
        field=None,
        field_applicable=None,
        inverse=None,
        is_instance_field=None,
        msg=None,
    ):
        return self.applicable(
            *responses,
            field=field,
            field_applicable=field_applicable,
            inverse=inverse,
            is_instance_field=is_instance_field,
            msg=msg,
        )

    def not_applicable_if(
        self,
        *responses,
        field=None,
        field_applicable=None,
        inverse=None,
        is_instance_field=None,
        msg=None,
    ):
        return self.not_applicable(
            *responses,
            field=field,
            field_applicable=field_applicable,
            inverse=inverse,
            is_instance_field=is_instance_field,
            msg=msg,
        )

    def not_applicable_only_if(
        self, *responses, field=None, field_applicable=None, is_instance_field=None
    ):

        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        field_value = self.get(field)
        field_applicable_value = self.get(field_applicable)

        if field_value in responses and (
            (field_applicable_value and field_applicable_value is not None)
        ):
            self.raise_not_applicable(field_applicable)

    def applicable(
        self,
        *responses,
        field=None,
        field_applicable=None,
        inverse=None,
        is_instance_field=None,
        msg=None,
    ):
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 applicable.
        """
        inverse = True if inverse is None else inverse
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if field in self.cleaned_data and field_applicable in self.cleaned_data:
            field_value = self.get(field)
            field_applicable_value = self.get(field_applicable)

            if field_value in responses and (
                field_applicable_value is None
                or field_applicable_value == NOT_APPLICABLE
            ):
                self.raise_applicable(field_applicable, msg=msg)
            elif (
                field_value not in responses
                and field_applicable_value != NOT_APPLICABLE
                and inverse
            ):
                self.raise_not_applicable(field_applicable, msg=msg)
        return False

    def not_applicable(
        self,
        *responses,
        field=None,
        field_applicable=None,
        inverse=None,
        is_instance_field=None,
        msg=None,
    ):
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 NOT applicable.
        """
        inverse = True if inverse is None else inverse
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if field in self.cleaned_data and field_applicable in self.cleaned_data:
            if (
                self.get(field) in responses
                and self.get(field_applicable) != NOT_APPLICABLE
            ):
                self.raise_not_applicable(field_applicable, msg=msg)
            elif inverse and (
                self.get(field) not in responses
                and self.get(field_applicable) == NOT_APPLICABLE
            ):
                self.raise_applicable(field_applicable)
        return False

    def applicable_if_true(
        self,
        condition,
        field_applicable=None,
        applicable_msg=None,
        not_applicable_msg=None,
    ):
        if field_applicable in self.cleaned_data:
            if condition and self.get(field_applicable) == NOT_APPLICABLE:
                self.raise_applicable(field_applicable, msg=applicable_msg)
            elif not condition and self.get(field_applicable) != NOT_APPLICABLE:
                self.raise_not_applicable(field_applicable, msg=not_applicable_msg)
