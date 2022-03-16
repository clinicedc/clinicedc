from edc_form_validators.base_form_validator import INVALID_ERROR, BaseFormValidator


class DateValidator(BaseFormValidator):
    def _date_is(self, op, field=None, reference_field=None, msg=None):
        operators = ["<", ">", "="]
        if op not in operators:
            raise TypeError(f"Invalid operator. Expected on of {operators}.")
        if self.cleaned_data.get(field) and self.cleaned_data.get(reference_field):
            try:
                value = eval(
                    f"{self.cleaned_data.get(field)}{op}"
                    f"{self.cleaned_data.get(reference_field).date()}"
                )
            except AttributeError:
                value = eval(
                    f"{self.cleaned_data.get(field)}{op}"
                    f"{self.cleaned_data.get(reference_field)}"
                )
            if value:
                self.raise_validation_error({field: msg}, INVALID_ERROR)

    def date_is_future(self, field=None, reference_field=None, msg=None, extra_msg=None):
        """Raises if date/datetime field is future relative
        to reference_field.
        """
        reference_field = reference_field or "report_datetime"
        msg = msg or f"Invalid. Expected a future date. {extra_msg or ''}".strip()
        self._date_is("<", field=field, reference_field=reference_field, msg=msg)

    def date_is_past(self, field=None, reference_field=None, msg=None, extra_msg=None):
        """Raises if date/datetime field is past relative
        to reference_field.
        """
        reference_field = reference_field or "report_datetime"
        msg = msg or f"Invalid. Expected a past date. {extra_msg or ''}".strip()
        self._date_is(">", field=field, reference_field=reference_field, msg=msg)

    def date_is_today(self, field=None, reference_field=None, msg=None, extra_msg=None):
        """Raises if date/datetime field is equal
        to reference_field.
        """
        reference_field = reference_field or "report_datetime"
        msg = msg or f"Invalid. Expected today. {extra_msg or ''}".strip()
        self._date_is("=", field=field, reference_field=reference_field, msg=msg)
