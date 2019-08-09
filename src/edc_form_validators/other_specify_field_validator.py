from django.forms import ValidationError
from edc_constants.constants import OTHER

from .base_form_validator import BaseFormValidator, NOT_REQUIRED_ERROR, REQUIRED_ERROR


class OtherSpecifyFieldValidator(BaseFormValidator):
    """A modelform mixin that handles 'OTHER/Other specify'
    field pattern.
    """

    def validate_other_specify(
        self,
        field,
        other_specify_field=None,
        required_msg=None,
        not_required_msg=None,
        other_stored_value=None,
        ref=None,
        fk_stored_field_name=None,
        **kwargs,
    ):
        """Returns False or raises a ValidationError.
        """
        cleaned_data = self.cleaned_data
        other = other_stored_value or OTHER
        if fk_stored_field_name is None:
            fk_stored_field_name = self.default_fk_stored_field_name

        # assume field naming convention
        if not other_specify_field:
            other_specify_field = f"{field}_other"

        # perhaps this is a list field / fk
        field_value = getattr(
            cleaned_data.get(field), fk_stored_field_name, cleaned_data.get(field)
        )

        if (
            field_value is not None
            and field_value == other
            and not cleaned_data.get(other_specify_field)
        ):
            ref = "" if not ref else f" ref: {ref}"
            message = {
                other_specify_field: required_msg or f"This field is required.{ref}"
            }
            self._errors.update(message)
            self._error_codes.append(REQUIRED_ERROR)
            raise ValidationError(message, code=REQUIRED_ERROR)
        elif (
            field_value is not None
            and field_value != other
            and cleaned_data.get(other_specify_field)
        ):
            ref = "" if not ref else f" ref: {ref}"
            message = {
                other_specify_field: not_required_msg
                or f"This field is not required.{ref}"
            }
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        elif field_value is None and cleaned_data.get(other_specify_field):
            ref = "" if not ref else f" ref: {ref}"
            message = {
                other_specify_field: not_required_msg
                or f"This field is not required.{ref}"
            }
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        return False
