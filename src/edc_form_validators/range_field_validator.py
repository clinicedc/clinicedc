import re

from .base_form_validator import BaseFormValidator, InvalidModelFormFieldValidator
from .base_form_validator import OUT_OF_RANGE_ERROR, REQUIRED_ERROR


class RangeFieldValidator(BaseFormValidator):
    def out_of_range_if(
        self,
        lower,
        upper,
        field=None,
        lower_inclusive=None,
        upper_inclusive=None,
        allow_none=None,
    ):
        r = re.compile(r"^\d*[.,]?\d*$")
        lower_inclusive = True if lower_inclusive is None else lower_inclusive
        upper_inclusive = True if upper_inclusive is None else upper_inclusive
        if not field:
            raise InvalidModelFormFieldValidator("The field attr cannot be None.")
        if self.cleaned_data:
            value = self.cleaned_data.get(field)
            if value is None and allow_none:
                pass
            elif value is None and not allow_none:
                self.raise_validation_error(
                    {field: "This field is required."}, REQUIRED_ERROR
                )
            elif r.match(str(value)):
                lower_op = "<" if not lower_inclusive else "<="
                upper_op = "<" if not upper_inclusive else "<="
                expression = f"{lower}{lower_op}{value}{upper_op}{upper}"
                if not eval(expression):
                    message = {
                        field: (
                            f"This field is not within range. Expected "
                            f"{expression}."
                        )
                    }
                    self.raise_validation_error(message, OUT_OF_RANGE_ERROR)
        return False
