from __future__ import annotations

from datetime import date, datetime

from django.conf import settings
from edc_constants.constants import EQ, GT, GTE, LT, LTE
from edc_utils import convert_php_dateformat
from edc_utils.date import to_local

from .base_form_validator import INVALID_ERROR, BaseFormValidator


class DateValidatorError(Exception):
    pass


class DateValidator(BaseFormValidator):
    def _date_is(
        self,
        op,
        field: str | None = None,
        reference_field: str = None,
        field_value: datetime | date | None = None,
        msg: str | None = None,
    ):
        operators = [LT, GT, EQ, LTE, GTE]
        if op not in operators:
            raise TypeError(f"Invalid operator. Expected on of {operators}.")
        if field and field_value:
            raise TypeError("Expected field name or field value but not both.")
        reference_value = self._get_as_date(reference_field or "report_datetime")
        field_value = self._get_as_date(field or field_value)
        if field_value and reference_value:
            if not self._compare_date_to_reference_value(op, field_value, reference_value):
                if field:
                    self.raise_validation_error({field: msg}, INVALID_ERROR)
                else:
                    self.raise_validation_error(msg, INVALID_ERROR)

    @staticmethod
    def _compare_date_to_reference_value(
        op: str,
        field_value: date,
        reference_value: date,
    ) -> bool:
        if op == LT:
            value = field_value < reference_value
        elif op == LTE:
            value = field_value >= reference_value
        elif op == GT:
            value = field_value > reference_value
        elif op == GTE:
            value = field_value >= reference_value
        elif op == EQ:
            value = field_value == reference_value
        else:
            raise DateValidatorError(f"Unknown operator. Got {op}.")
        return value

    def _get_as_date(self, key_or_value: str | date | datetime) -> date | None:
        """Returns a date or None using either a key or value.

        * If key is given, gets value from cleaned data.
        * Ensures a datetime is localized before converting to date.
        """
        try:
            value = self.cleaned_data.get(key_or_value)
        except KeyError:
            value = key_or_value
        if value:
            try:
                value.date()
            except AttributeError:
                pass
            else:
                value = to_local(value).date()
        return value

    def date_is_future_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is future relative
        to reference_field.
        """
        msg = msg or f"Invalid. Expected a future date. {extra_msg or ''}".strip()
        self._date_is(
            GT, field=field, reference_field=reference_field, field_value=field_value, msg=msg
        )

    def date_is_past_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is past relative
        to reference_field.
        """
        msg = msg or f"Invalid. Expected a past date. {extra_msg or ''}".strip()
        self._date_is(
            LT, field=field, reference_field=reference_field, field_value=field_value, msg=msg
        )

    def date_is_equal_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is equal
        to reference_field.
        """
        msg = msg or f"Invalid. Expected dates to match. {extra_msg or ''}".strip()
        self._date_is(
            EQ, field=field, reference_field=reference_field, field_value=field_value, msg=msg
        )

    def date_before_report_datetime_or_raise(
        self,
        field=None,
        report_datetime_field=None,
    ):
        """Convenience method if comparing with report_datetime."""
        msg = None
        report_datetime_field = report_datetime_field or "report_datetime"
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            msg = f"Invalid. Cannot be before report date/time. Got {dte}"
        return self.date_is_past_or_raise(
            field=field,
            reference_field=report_datetime_field,
            msg=msg,
        )

    def date_after_report_datetime_or_raise(
        self,
        field=None,
        report_datetime_field=None,
    ):
        """Convenience method if comparing with report_datetime."""
        msg = None
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            msg = f"Invalid. Cannot be after report date/time. Got {dte}"
        return self.date_is_future_or_raise(
            field=field,
            reference_field=report_datetime_field,
            msg=msg,
        )
