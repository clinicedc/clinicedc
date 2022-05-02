from datetime import date, datetime
from typing import Optional, Union

from django.conf import settings
from edc_utils import convert_php_dateformat

from edc_form_validators.base_form_validator import INVALID_ERROR, BaseFormValidator


class DateValidator(BaseFormValidator):
    def _date_is(
        self,
        op,
        field: Optional[str] = None,
        reference_field: Optional[str] = None,
        msg: Optional[str] = None,
    ):
        operators = ["<", ">", "="]
        if op not in operators:
            raise TypeError(f"Invalid operator. Expected on of {operators}.")
        if self.cleaned_data.get(field) and self.cleaned_data.get(reference_field):
            try:
                date_value = self.cleaned_data.get(field).date()
            except AttributeError:
                date_value = self.cleaned_data.get(field)
            try:
                reference_value = self.cleaned_data.get(reference_field).date()
            except AttributeError:
                reference_value = self.cleaned_data.get(reference_field)
            value = self.compare_to_reference_value(op, reference_value, date_value)
            if value:
                self.raise_validation_error({field: msg}, INVALID_ERROR)

    @staticmethod
    def compare_to_reference_value(
        op: str, reference_value: Union[date, datetime], date_value: date
    ) -> Optional[bool]:
        value = None
        if op == "<":
            value = reference_value < date_value
        elif op == ">":
            value = reference_value > date_value
        elif op == "=":
            value = reference_value == date_value
        return value

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

    def invalid_if_before_report_datetime(self, field=None, report_datetime_field=None):
        msg = None
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            msg = f"Invalid. Cannot be before report date/time. Got {dte}"
        return self.date_is_past(field=field, reference_field=report_datetime_field, msg=msg)

    def invalid_if_after_report_datetime(self, field=None, report_datetime_field=None):
        msg = None
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            msg = f"Invalid. Cannot be after report date/time. Got {dte}"
        return self.date_is_future(field=field, reference_field=report_datetime_field, msg=msg)
