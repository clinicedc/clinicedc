from copy import copy
from typing import Optional, Union

from edc_constants.constants import DWTA, NOT_APPLICABLE

from .base_form_validator import (
    NOT_REQUIRED_ERROR,
    REQUIRED_ERROR,
    BaseFormValidator,
    InvalidModelFormFieldValidator,
)


class RequiredFieldValidator(BaseFormValidator):
    def raise_required(
        self, field: str, msg: Optional[str] = None, inline_set: Optional[str] = None
    ) -> None:
        if inline_set:
            message = {
                "__all__": (
                    msg or "Based on your responses, inline information is required."
                ).strip()
            }
        else:
            message = {field: f"This field is required. {msg or ''}".strip()}
        self.raise_validation_error(message, REQUIRED_ERROR)
        return None

    def raise_not_required(
        self, field: str, msg: Optional[str] = None, inline_set: Optional[str] = None
    ) -> None:
        if inline_set:
            message = {
                "__all__": (
                    msg or "Based on your responses, inline information is not required."
                ).strip()
            }
        else:
            message = {field: f"This field is not required. {msg or ''}".strip()}
        self.raise_validation_error(message, NOT_REQUIRED_ERROR)
        return None

    def required_if(
        self,
        *responses: Union[str, int, bool],
        field: str = None,
        field_required: str = None,
        required_msg: Optional[str] = None,
        not_required_msg: Optional[str] = None,
        optional_if_dwta: Optional[bool] = None,
        optional_if_na: Optional[bool] = None,
        inverse: Optional[bool] = None,
        is_instance_field: Optional[bool] = None,
        field_required_evaluate_as_int: Optional[bool] = None,
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

        if field_required_evaluate_as_int:
            field_required_has_value = (
                self.get(field_required, inline_set=inline_set) is not None
            )
        else:
            field_required_has_value = self.get(field_required, inline_set=inline_set)

        if field in self.cleaned_data:
            if DWTA in responses and optional_if_dwta and field_value == DWTA:
                pass
            elif (
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
        field_required: str = None,
        required_msg: Optional[str] = None,
        not_required_msg: Optional[str] = None,
        inverse: Optional[bool] = None,
    ) -> bool:
        inverse = True if inverse is None else inverse
        if not field_required:
            raise InvalidModelFormFieldValidator("The required field cannot be None.")
        if self.cleaned_data and field_required in self.cleaned_data:
            if condition and (
                self.cleaned_data.get(field_required) is None
                or self.cleaned_data.get(field_required) == ""
                or self.cleaned_data.get(field_required) == NOT_APPLICABLE
            ):
                self.raise_required(field=field_required, msg=required_msg)
            elif inverse and (
                not condition
                and self.cleaned_data.get(field_required) is not None
                and self.cleaned_data.get(field_required) != ""
                and self.cleaned_data.get(field_required) != NOT_APPLICABLE
            ):
                self.raise_not_required(field=field_required, msg=not_required_msg)
        return False

    def not_required_if_true(
        self,
        condition: bool,
        field: str = None,
        msg: Optional[str] = None,
        is_instance_field: Optional[bool] = None,
    ) -> bool:
        """Raises a ValidationError if condition is True stating the
        field is NOT required.

        The inverse is not tested.
        """
        if not field:
            raise InvalidModelFormFieldValidator("The required field cannot be None.")
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
        field: str = None,
        field_required: str = None,
        required_msg: Optional[str] = None,
        not_required_msg: Optional[str] = None,
        optional_if_dwta: Optional[bool] = None,
        inverse: Optional[bool] = None,
        field_required_evaluate_as_int: Optional[bool] = None,
        is_instance_field: Optional[bool] = None,
    ) -> bool:
        """Raises an exception or returns False.

        If field is not none, field_required is "required".
        """
        inverse = True if inverse is None else inverse
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if not field_required:
            raise InvalidModelFormFieldValidator("The required field cannot be None.")
        if optional_if_dwta and self.cleaned_data.get(field) == DWTA:
            field_value = None
        else:
            field_value = self.cleaned_data.get(field)

        if field_required_evaluate_as_int:
            field_required_has_value = self.cleaned_data.get(field_required) is not None
        else:
            field_required_has_value = self.cleaned_data.get(field_required)

        if field_value is not None and not field_required_has_value:
            self.raise_required(field=field_required, msg=required_msg)
        elif (
            field_value is None
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
        *responses: Union[str, int, bool],
        field: str = None,
        field_required: str = None,
        field_not_required: Optional[str] = None,
        required_msg: Optional[str] = None,
        not_required_msg: Optional[str] = None,
        optional_if_dwta: Optional[bool] = None,
        inverse: Optional[bool] = None,
        is_instance_field: Optional[bool] = None,
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
        field: str = None,
        field_required: str = None,
        required_msg: Optional[str] = None,
        is_instance_field: Optional[bool] = None,
    ) -> bool:
        """Required `b` if `a`; do not require `b` if not `a`"""
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        if (
            self.cleaned_data.get(field) is not None
            and self.cleaned_data.get(field_required) is None
        ):
            self.raise_required(field=field_required, msg=required_msg)
        elif (
            self.cleaned_data.get(field) is None
            and self.cleaned_data.get(field_required) is not None
        ):
            self.raise_not_required(field=field_required, msg=required_msg)
        return False

    @staticmethod
    def _inspect_params(
        *responses: Union[str, int, bool], field: str = None, field_required: str = None
    ) -> bool:
        """Inspects params and raises if any are None"""
        if not field:
            raise InvalidModelFormFieldValidator('"field" cannot be None.')
        elif not responses:
            raise InvalidModelFormFieldValidator(
                f"At least one valid response for field '{field}' must be provided."
            )
        elif not field_required:
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
