from django.forms import ValidationError
from edc_constants.constants import NOT_APPLICABLE

from .base_form_validator import BaseFormValidator
from .base_form_validator import APPLICABLE_ERROR, NOT_APPLICABLE_ERROR


class ApplicableFieldValidator(BaseFormValidator):

    def applicable_if(self, *responses, field=None, field_applicable=None):
        return self.applicable(
            *responses, field=field, field_applicable=field_applicable)

    def not_applicable_if(self, *responses, field=None, field_applicable=None):
        return self.not_applicable(
            *responses, field=field, field_applicable=field_applicable)

    def not_applicable_only_if(self, *responses, field=None,
                               field_applicable=None, cleaned_data=None):

        cleaned_data = self.cleaned_data
        if (cleaned_data.get(field) in responses
            and ((cleaned_data.get(field_applicable)
                  and cleaned_data.get(field_applicable) is not None))):
            message = {
                field_applicable: 'This field is not required.'}
            self._errors.update(message)
            self._error_codes.append(NOT_APPLICABLE_ERROR)
            raise ValidationError(message, code=NOT_APPLICABLE_ERROR)

    def applicable(self, *responses, field=None, field_applicable=None):
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 applicable.
        """
        cleaned_data = self.cleaned_data
        if field in cleaned_data and field_applicable in cleaned_data:
            if (cleaned_data.get(field) in responses
                    and cleaned_data.get(field_applicable) == NOT_APPLICABLE):
                message = {field_applicable: 'This field is applicable'}
                self._errors.update(message)
                self._error_codes.append(APPLICABLE_ERROR)
                raise ValidationError(message, code=APPLICABLE_ERROR)
            elif (cleaned_data.get(field) not in responses
                    and cleaned_data.get(field_applicable) != NOT_APPLICABLE):
                message = {field_applicable: 'This field is not applicable'}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
        return False

    def not_applicable(self, *responses, field=None, field_applicable=None):
        """Returns False or raises a validation error for field
        pattern where response to question 1 makes
        question 2 NOT applicable.
        """
        cleaned_data = self.cleaned_data
        if field in cleaned_data and field_applicable in cleaned_data:
            if (cleaned_data.get(field) in responses
                    and cleaned_data.get(field_applicable) != NOT_APPLICABLE):
                message = {field_applicable: 'This field is not applicable'}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
            elif (cleaned_data.get(field) not in responses
                    and cleaned_data.get(field_applicable) == NOT_APPLICABLE):
                message = {field_applicable: 'This field is applicable'}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
        return False

    def applicable_if_true(self, condition, field_applicable=None,
                           applicable_msg=None, not_applicable_msg=None,
                           **kwargs):
        cleaned_data = self.cleaned_data
        if field_applicable in cleaned_data:
            if (condition
                    and self.cleaned_data.get(field_applicable) == NOT_APPLICABLE):
                message = {field_applicable: 'This field is applicable'}
                self._errors.update(message)
                self._error_codes.append(APPLICABLE_ERROR)
                raise ValidationError(message, code=APPLICABLE_ERROR)
            elif (not condition
                  and self.cleaned_data.get(field_applicable) != NOT_APPLICABLE):
                message = {field_applicable: 'This field is not applicable'}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
