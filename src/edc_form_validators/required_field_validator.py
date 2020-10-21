from edc_constants.constants import DWTA, NOT_APPLICABLE

from .base_form_validator import BaseFormValidator, InvalidModelFormFieldValidator
from .base_form_validator import REQUIRED_ERROR, NOT_REQUIRED_ERROR


class RequiredFieldValidator(BaseFormValidator):
    def raise_required(self, field, msg=None):
        message = {field: f"This field is required. {msg or ''}".strip()}
        self.raise_validation_error(message, REQUIRED_ERROR)

    def raise_not_required(self, field, msg=None):
        message = {field: f"This field is not required. {msg or ''}".strip()}
        self.raise_validation_error(message, NOT_REQUIRED_ERROR)

    def required_if(
        self,
        *responses,
        field=None,
        field_required=None,
        required_msg=None,
        not_required_msg=None,
        optional_if_dwta=None,
        optional_if_na=None,
        inverse=None,
        is_instance_field=None,
        field_required_evaluate_as_int=None,
    ):
        """Raises an exception or returns False.

        if field in responses then field_required is required.
        """
        inverse = True if inverse is None else inverse
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        self._inspect_params(*responses, field=field, field_required=field_required)
        field_value = self.get(field)

        if field_required_evaluate_as_int:
            field_required_has_value = self.cleaned_data.get(field_required) is not None
        else:
            field_required_has_value = self.cleaned_data.get(field_required)

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
                or self.cleaned_data.get(field_required) == NOT_APPLICABLE
            ):
                self.raise_required(field=field_required, msg=required_msg)
            elif inverse and (
                field_value not in responses
                and (
                    field_required_has_value
                    and (self.cleaned_data.get(field_required) != NOT_APPLICABLE)
                )
            ):
                self.raise_not_required(field=field_required, msg=not_required_msg)
        return False

    def required_if_true(
        self,
        condition,
        field_required=None,
        required_msg=None,
        not_required_msg=None,
        inverse=None,
    ):
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

    def not_required_if_true(
        self, condition, field=None, msg=None, is_instance_field=None
    ):
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

    def required_if_not_none(
        self,
        field=None,
        field_required=None,
        required_msg=None,
        not_required_msg=None,
        optional_if_dwta=None,
        inverse=None,
        field_required_evaluate_as_int=None,
        is_instance_field=None,
    ):
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

    def required_integer_if_not_none(self, **kwargs):
        """Raises an exception or returns False.

        Evaluates the value of field required as an integer, that is,
        0 is not None.
        """
        self.required_if_not_none(field_required_evaluate_as_int=True, **kwargs)

    def not_required_if(
        self,
        *responses,
        field=None,
        field_required=None,
        field_not_required=None,
        required_msg=None,
        not_required_msg=None,
        optional_if_dwta=None,
        inverse=None,
        is_instance_field=None,
    ):
        """Raises an exception or returns False.

        if field NOT in responses then field_required is required.
        """
        inverse = True if inverse is None else inverse
        field_required = field_required or field_not_required
        if is_instance_field:
            self.update_cleaned_data_from_instance(field)
        self._inspect_params(*responses, field=field, field_required=field_required)
        if field in self.cleaned_data and field_required in self.cleaned_data:
            if (
                DWTA in responses
                and optional_if_dwta
                and self.cleaned_data.get(field) == DWTA
            ):
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
        self, field=None, field_required=None, required_msg=None, is_instance_field=None
    ):
        """Required b if a. Do not require b if not a.
        """
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

    @staticmethod
    def _inspect_params(*responses, field=None, field_required=None):
        """Inspects params and raises if any are None.
        """
        if not field:
            raise InvalidModelFormFieldValidator('"field" cannot be None.')
        elif not responses:
            raise InvalidModelFormFieldValidator(
                f"At least one valid response for field '{field}' must be provided."
            )
        elif not field_required:
            raise InvalidModelFormFieldValidator('"field_required" cannot be None.')
