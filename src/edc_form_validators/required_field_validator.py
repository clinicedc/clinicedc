from django.forms import ValidationError
from edc_constants.constants import DWTA, NOT_APPLICABLE

from .base_form_validator import BaseFormValidator, InvalidModelFormFieldValidator
from .base_form_validator import REQUIRED_ERROR, NOT_REQUIRED_ERROR


class RequiredFieldValidator(BaseFormValidator):

    def required_if(self, *responses, field=None, field_required=None,
                    required_msg=None, not_required_msg=None,
                    optional_if_dwta=None, optional_if_na=None,
                    inverse=None,
                    code=None, **kwargs):
        """Raises an exception or returns False.

        if field in responses then field_required is required.
        """
        inverse = True if inverse is None else inverse
        self._inspect_params(
            *responses, field=field, field_required=field_required)
        if field in self.cleaned_data:
            if (DWTA in responses and optional_if_dwta
                    and self.cleaned_data.get(field) == DWTA):
                pass
            elif (NOT_APPLICABLE in responses and optional_if_na
                    and self.cleaned_data.get(field) == NOT_APPLICABLE):
                pass
            elif (self.cleaned_data.get(field) in responses
                    and (not self.cleaned_data.get(field_required)
                         or self.cleaned_data.get(field_required) == NOT_APPLICABLE)):
                message = {
                    field_required: required_msg or 'This field is required.'}
                self._errors.update(message)
                self._error_codes.append(REQUIRED_ERROR)
                raise ValidationError(message, code=REQUIRED_ERROR)
            elif inverse and (self.cleaned_data.get(field) not in responses
                              and (self.cleaned_data.get(field_required)
                                   and (self.cleaned_data.get(field_required)
                                        != NOT_APPLICABLE))):
                message = {
                    field_required: not_required_msg or 'This field is not required.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        return False

    def required_if_true(self, condition, field_required=None,
                         required_msg=None, not_required_msg=None,
                         code=None, inverse=None, **kwargs):
        inverse = True if inverse is None else inverse
        if not field_required:
            raise InvalidModelFormFieldValidator(
                f'The required field cannot be None.')
        if self.cleaned_data and field_required in self.cleaned_data:
            if (condition and (not self.cleaned_data.get(field_required)
                               or self.cleaned_data.get(field_required) == NOT_APPLICABLE)):
                message = {
                    field_required: required_msg or 'This field is required.'}
                self._errors.update(message)
                self._error_codes.append(REQUIRED_ERROR)
                raise ValidationError(message, code=REQUIRED_ERROR)
            elif inverse and (not condition and self.cleaned_data.get(field_required)
                              and self.cleaned_data.get(field_required) != NOT_APPLICABLE):
                message = {
                    field_required: not_required_msg or 'This field is not required.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)

    def required_if_not_none(self, field=None, field_required=None,
                             required_msg=None, not_required_msg=None,
                             optional_if_dwta=None, **kwargs):
        """Raises an exception or returns False.

        If field is not none, field_required is "required".
        """
        if not field_required:
            raise InvalidModelFormFieldValidator(
                f'The required field cannot be None.')
        if optional_if_dwta and self.cleaned_data.get(field) == DWTA:
            condition = None
        else:
            condition = self.cleaned_data.get(field) is not None
        if condition and not self.cleaned_data.get(field_required):
            message = {
                field_required: required_msg or 'This field is required.'}
            self._errors.update(message)
            self._error_codes.append(REQUIRED_ERROR)
            raise ValidationError(message, code=REQUIRED_ERROR)
        elif (not condition and self.cleaned_data.get(field_required)
              and self.cleaned_data.get(field_required) != NOT_APPLICABLE):
            message = {
                field_required: not_required_msg or 'This field is not required.'}
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)

    def not_required_if(self, *responses, field=None, field_required=None,
                        required_msg=None, not_required_msg=None,
                        optional_if_dwta=None, inverse=None, code=None, **kwargs):
        """Raises an exception or returns False.

        if field NOT in responses then field_required is required.
        """
        inverse = True if inverse is None else inverse
        self._inspect_params(
            *responses, field=field, field_required=field_required)
        if field in self.cleaned_data and field_required in self.cleaned_data:
            if (DWTA in responses and optional_if_dwta
                    and self.cleaned_data.get(field) == DWTA):
                pass
            elif (self.cleaned_data.get(field) in responses
                    and (self.cleaned_data.get(field_required)
                         and self.cleaned_data.get(field_required) != NOT_APPLICABLE)):
                message = {
                    field_required: not_required_msg or 'This field is not required.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)
            elif inverse and (self.cleaned_data.get(field) not in responses
                              and (not self.cleaned_data.get(field_required)
                                   or (self.cleaned_data.get(field_required)
                                       == NOT_APPLICABLE))):
                message = {
                    field_required: required_msg or 'This field is required.'}
                self._errors.update(message)
                self._error_codes.append(REQUIRED_ERROR)
                raise ValidationError(message, code=REQUIRED_ERROR)
        return False

    def require_together(self, field=None, field_required=None, required_msg=None):
        """Required b if a. Do not require b if not a.
        """
        if (self.cleaned_data.get(field) is not None
                and self.cleaned_data.get(field_required) is None):
            message = {
                field_required: required_msg or 'This field is required.'}
            self._errors.update(message)
            self._error_codes.append(REQUIRED_ERROR)
            raise ValidationError(message, code=REQUIRED_ERROR)
        elif (self.cleaned_data.get(field) is None
                and self.cleaned_data.get(field_required) is not None):
            message = {
                field_required: required_msg or 'This field is not required.'}
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)

    def _inspect_params(self, *responses, field=None, field_required=None):
        """Inspects params and raises if any are None.
        """
        if not field:
            raise InvalidModelFormFieldValidator(f'"field" cannot be None.')
        elif not responses:
            raise InvalidModelFormFieldValidator(
                f'At least one valid response for field \'{field}\' must be provided.')
        elif not field_required:
            raise InvalidModelFormFieldValidator(
                f'"field_required" cannot be None.')
