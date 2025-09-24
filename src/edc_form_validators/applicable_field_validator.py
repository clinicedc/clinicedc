from typing import Any

from edc_constants.constants import NOT_APPLICABLE, NULL_STRING

from .base_form_validator import (
    APPLICABLE_ERROR,
    NOT_APPLICABLE_ERROR,
    BaseFormValidator,
)


class ApplicableFieldValidator(BaseFormValidator):
    def raise_applicable(
        self,
        field,
        msg: str | None = None,
        applicable_msg: str | None = None,
    ) -> None:
        message = {field: applicable_msg or f"This field is applicable. {msg or ''}".strip()}
        self.raise_validation_error(message, APPLICABLE_ERROR)

    def raise_not_applicable(
        self,
        field,
        msg: str | None = None,
        not_applicable_msg: str | None = None,
    ) -> None:
        message = {
            field: not_applicable_msg or f"This field is not applicable. {msg or ''}".strip()
        }
        self.raise_validation_error(message, NOT_APPLICABLE_ERROR)

    def applicable_if(
        self,
        *responses: Any,
        field: str,
        field_applicable: str,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
        msg: str | None = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        not_applicable_value=None,
    ) -> bool:
        return self.applicable(
            *responses,
            field=field,
            field_applicable=field_applicable,
            inverse=inverse,
            is_instance_field=is_instance_field,
            msg=msg,
            applicable_msg=applicable_msg,
            not_applicable_msg=not_applicable_msg,
            not_applicable_value=not_applicable_value,
        )

    def not_applicable_if(
        self,
        *responses: Any,
        field: str = None,
        field_applicable: str = None,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
        msg: str | None = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        not_applicable_value=None,
    ) -> bool:
        return self.not_applicable(
            *responses,
            field=field,
            field_applicable=field_applicable,
            inverse=inverse,
            is_instance_field=is_instance_field,
            msg=msg,
            applicable_msg=applicable_msg,
            not_applicable_msg=not_applicable_msg,
            not_applicable_value=not_applicable_value,
        )

    def not_applicable_only_if(
        self, *responses, field=None, field_applicable=None, is_instance_field=None
    ) -> bool:
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        field_value = self.get(field)
        field_applicable_value = self.get(field_applicable)

        if field_value in responses and (
            field_applicable_value and field_applicable_value is not None
        ):
            self.raise_not_applicable(field_applicable)
        return False

    def applicable(
        self,
        *responses: Any,
        field: str,
        field_applicable: str,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
        msg: str | None = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        not_applicable_value=None,
    ) -> bool:
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 applicable.
        """
        inverse = True if inverse is None else inverse
        not_applicable = not_applicable_value or NOT_APPLICABLE
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if field in self.cleaned_data and field_applicable in self.cleaned_data:
            field_value = self.get(field)
            field_applicable_value = self.get(field_applicable)

            if field_value in responses and (
                field_applicable_value in (None, NULL_STRING, not_applicable)
            ):
                self.raise_applicable(field_applicable, msg=msg, applicable_msg=applicable_msg)
            elif (
                field_value not in responses
                and field_applicable_value != not_applicable
                and inverse
            ):
                self.raise_not_applicable(
                    field_applicable, msg=msg, not_applicable_msg=not_applicable_msg
                )
        return False

    def not_applicable(
        self,
        *responses: Any,
        field: str = None,
        field_applicable: str = None,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
        msg: str | None = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        not_applicable_value=None,
    ) -> bool:
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 NOT applicable.
        """
        inverse = True if inverse is None else inverse
        not_applicable = not_applicable_value or NOT_APPLICABLE
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if field in self.cleaned_data and field_applicable in self.cleaned_data:
            if self.get(field) in responses and self.get(field_applicable) != not_applicable:
                self.raise_not_applicable(
                    field_applicable, msg=msg, not_applicable_msg=not_applicable_msg
                )
            elif inverse and (
                self.get(field) not in responses
                and self.get(field_applicable) == not_applicable
            ):
                self.raise_applicable(field_applicable, msg=msg, applicable_msg=applicable_msg)
        return False

    def applicable_if_true(
        self,
        condition: bool,
        field_applicable: str = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        inverse: bool | None = None,
        not_applicable_value=None,
    ) -> bool:
        inverse = True if inverse is None else inverse
        not_applicable = not_applicable_value or NOT_APPLICABLE
        if field_applicable in self.cleaned_data:
            if condition and self.get(field_applicable) == not_applicable:
                self.raise_applicable(field_applicable, msg=applicable_msg)
            elif not condition and self.get(field_applicable) != not_applicable:
                if inverse:
                    self.raise_not_applicable(
                        field_applicable,
                        not_applicable_msg=not_applicable_msg,
                        msg=not_applicable_msg,
                    )
        return False

    def not_applicable_if_true(
        self,
        condition: bool,
        field_applicable: str = None,
        applicable_msg: str | None = None,
        not_applicable_msg: str | None = None,
        inverse: bool | None = None,
        not_applicable_value=None,
    ) -> bool:
        inverse = True if inverse is None else inverse
        not_applicable = not_applicable_value or NOT_APPLICABLE
        if field_applicable in self.cleaned_data:
            if condition and self.get(field_applicable) != not_applicable:
                self.raise_not_applicable(field_applicable, msg=not_applicable_msg)
            elif not condition and self.get(field_applicable) == not_applicable:
                if inverse:
                    self.raise_applicable(
                        field_applicable,
                        applicable_msg=applicable_msg,
                        msg=applicable_msg,
                    )
        return False
