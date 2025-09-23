from copy import copy

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from edc_constants.constants import DWTA, NOT_APPLICABLE, NULL_STRING

from .base_form_validator import (
    NOT_REQUIRED_ERROR,
    REQUIRED_ERROR,
    BaseFormValidator,
    InvalidModelFormFieldValidator,
)


class RequiredFieldValidatorError(Exception):
    pass


class RequiredFieldValidator(BaseFormValidator):
    def raise_required(
        self, field: str, msg: str | None = None, inline_set: str | None = None
    ) -> None:
        if inline_set:
            default_errmsg = _("Based on your responses, inline information is required.")
            message = {"__all__": (msg or default_errmsg).strip()}
        else:
            errmsg = _("This field is required")
            message = {field: f"{errmsg}. {msg or ''}".strip()}
        self.raise_validation_error(message, REQUIRED_ERROR)

    def raise_not_required(
        self, field: str, msg: str | None = None, inline_set: str | None = None
    ) -> None:
        if inline_set:
            default_errmsg = _("Based on your responses, inline information is not required.")
            message = {"__all__": (msg or default_errmsg).strip()}
        else:
            errmsg = _("This field is not required")
            message = {field: f"{errmsg}. {msg or ''}".strip()}
        self.raise_validation_error(message, NOT_REQUIRED_ERROR)

    def required_if(
        self,
        *responses: str | int | bool,
        field: str,
        field_required: str,
        required_msg: str | None = None,
        not_required_msg: str | None = None,
        optional_if_dwta: bool | None = None,
        optional_if_na: bool | None = None,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
        field_required_evaluate_as_int: bool | None = None,
        fk_stored_field_name=None,
        field_required_inline_set=None,
    ) -> bool:
        """Raises an exception or returns False.

        if field in responses then field_required is required.

        is_instance_field: value comes from the model instance and not cleaned data
        """
        inverse = True if inverse is None else inverse
        inline_set = field_required_inline_set
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        responses = self._convert_response_to_values_if_instances(
            responses, fk_stored_field_name
        )
        self._inspect_params(*responses, field=field, field_required=field_required)
        field_value = self.get(field)

        if isinstance(field_value, (QuerySet,)):
            raise RequiredFieldValidatorError(
                "Field value is a QuerySet, is this an M2M? "
                f"Field='{field}'. See {self.__class__.__name__}."
            )

        if field_required_evaluate_as_int:
            field_required_has_value = (
                self.get(field_required, inline_set=inline_set) is not None
            )
        else:
            field_required_has_value = bool(self.get(field_required, inline_set=inline_set))

        if field in self.cleaned_data:
            if (DWTA in responses and optional_if_dwta and field_value == DWTA) or (
                NOT_APPLICABLE in responses
                and optional_if_na
                and field_value == NOT_APPLICABLE
            ):
                pass
            elif field_value in responses and (
                not field_required_has_value
                or self.get(field_required, inline_set=inline_set) == NOT_APPLICABLE
            ):
                self.raise_required(
                    field=field_required,
                    msg=required_msg,
                    inline_set=inline_set,
                )
            elif inverse and (
                field_value not in responses
                and (
                    field_required_has_value
                    and (self.get(field_required, inline_set=inline_set) != NOT_APPLICABLE)
                )
            ):
                self.raise_not_required(
                    field=field_required,
                    msg=not_required_msg,
                    inline_set=inline_set,
                )
        return False

    def required_if_true(
        self,
        condition: bool,
        field_required: str,
        required_msg: str | None = None,
        not_required_msg: str | None = None,
        inverse: bool | None = None,
    ) -> bool:
        inverse = True if inverse is None else inverse
        if not field_required:
            errmsg = _("The required field cannot be None.")
            raise InvalidModelFormFieldValidator(errmsg)
        if self.cleaned_data and field_required in self.cleaned_data:
            if condition and (
                self.cleaned_data.get(field_required) in [None, NULL_STRING, NOT_APPLICABLE]
            ):
                self.raise_required(field=field_required, msg=required_msg)
            elif inverse and (
                not condition
                and self.cleaned_data.get(field_required)
                not in [None, NULL_STRING, NOT_APPLICABLE]
            ):
                self.raise_not_required(field=field_required, msg=not_required_msg)
        return False

    def not_required_if_true(
        self,
        condition: bool,
        field: str,
        msg: str | None = None,
        is_instance_field: bool | None = None,
    ) -> bool:
        """Raises a ValidationError if condition is True stating the
        field is NOT required.

        The inverse is not tested.
        """
        if not field:
            errmsg = _("The required field cannot be None.")
            raise InvalidModelFormFieldValidator(errmsg)
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if self.cleaned_data and field in self.cleaned_data:
            try:
                field_value = self.cleaned_data.get(field).name
            except AttributeError:
                field_value = self.cleaned_data.get(field)
            if condition and field_value is not None and field_value != NOT_APPLICABLE:
                self.raise_not_required(field=field, msg=msg)
        return False

    def required_if_not_none(
        self,
        field: str,
        field_required: str,
        required_msg: str | None = None,
        not_required_msg: str | None = None,
        optional_if_dwta: bool | None = None,
        inverse: bool | None = None,
        field_required_evaluate_as_int: bool | None = None,
        is_instance_field: bool | None = None,
    ) -> bool:
        """Raises an exception or returns False.

        If field is not none, field_required is "required".

        Note: CharFields usually default to an empty string and not NULL.
           For IntegerFields, zero is a value.
        """
        inverse = True if inverse is None else inverse
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if not field_required:
            errmsg = _("The required field cannot be None.")
            raise InvalidModelFormFieldValidator(errmsg)
        if optional_if_dwta and self.cleaned_data.get(field) == DWTA:
            field_value = None
        else:
            field_value = self.cleaned_data.get(field)

        if field_required_evaluate_as_int:
            field_required_has_value = self.cleaned_data.get(field_required) not in [
                None,
                NULL_STRING,
            ]
        else:
            field_required_has_value = bool(self.cleaned_data.get(field_required))

        if field_value not in [None, NULL_STRING] and not field_required_has_value:
            self.raise_required(field=field_required, msg=required_msg)
        elif (
            field_value in [None, NULL_STRING]
            and field_required_has_value
            and self.cleaned_data.get(field_required) != NOT_APPLICABLE
            and inverse
        ):
            self.raise_not_required(field=field_required, msg=not_required_msg)
        return False

    def required_integer_if_not_none(self, **kwargs):
        """Raises an exception or returns False.

        Evaluates the value of field required as an integer, that is,
        0 is not None.
        """
        return self.required_if_not_none(field_required_evaluate_as_int=True, **kwargs)

    def not_required_if(
        self,
        *responses: str | int | bool,
        field: str,
        field_required: str | None = None,
        field_not_required: str | None = None,
        required_msg: str | None = None,
        not_required_msg: str | None = None,
        optional_if_dwta: bool | None = None,
        inverse: bool | None = None,
        is_instance_field: bool | None = None,
    ) -> bool:
        """Raises an exception or returns False.

        if field NOT in responses then field_required is required.
        """
        inverse = True if inverse is None else inverse
        field_required = field_required or field_not_required
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        self._inspect_params(*responses, field=field, field_required=field_required)
        if field in self.cleaned_data and field_required in self.cleaned_data:
            if DWTA in responses and optional_if_dwta and self.cleaned_data.get(field) == DWTA:
                pass
            elif self.cleaned_data.get(field) in responses and (
                self.cleaned_data.get(field_required)
                and self.cleaned_data.get(field_required) != NOT_APPLICABLE
            ):
                self.raise_not_required(field=field_required, msg=not_required_msg)
            elif inverse and (
                self.cleaned_data.get(field) not in responses
                and (
                    not self.cleaned_data.get(field_required)
                    or (self.cleaned_data.get(field_required) == NOT_APPLICABLE)
                )
            ):
                self.raise_required(field=field_required, msg=required_msg)
        return False

    def require_together(
        self,
        field: str,
        field_required: str,
        required_msg: str | None = None,
        is_instance_field: bool | None = None,
    ) -> bool:
        """Required `b` if `a`; do not require `b` if not `a`"""
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if self.cleaned_data.get(field) is not None and self.cleaned_data.get(
            field_required
        ) in [None, NULL_STRING]:
            self.raise_required(field=field_required, msg=required_msg)
        elif (
            self.cleaned_data.get(field) in [None, NULL_STRING]
            and self.cleaned_data.get(field_required) is not None
        ):
            self.raise_not_required(field=field_required, msg=required_msg)
        return False

    @staticmethod
    def _inspect_params(*responses: str | int | bool, field: str, field_required: str) -> bool:
        """Inspects params and raises if any are None"""
        if not field:
            errmsg = _("`field` cannot be `None`")
            raise InvalidModelFormFieldValidator(f"{errmsg}.")
        if not responses:
            errmsg = _(
                "At least one valid response for field '{field}' must be provided."
            ).format(field=field)
            raise InvalidModelFormFieldValidator(errmsg)
        if not field_required:
            raise InvalidModelFormFieldValidator('"field_required" cannot be None.')
        return False

    @staticmethod
    def _convert_response_to_values_if_instances(responses, fk_stored_field_name):
        fk_stored_field_name = fk_stored_field_name or "name"
        responses = list(responses)
        _responses = copy(responses)
        for index, response in enumerate(_responses):
            responses[index] = getattr(response, fk_stored_field_name, response)
        return tuple(responses)
