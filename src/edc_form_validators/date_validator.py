from __future__ import annotations

from datetime import date, datetime

from django.conf import settings

from edc_constants.constants import EQ, GT, GTE, LT, LTE
from edc_model import estimated_date_from_ago
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
        reference_value: datetime | date | None = None,
        msg: str | None = None,
    ):
        operators = [LT, GT, EQ, LTE, GTE]
        if op not in operators:
            raise TypeError(f"Invalid operator. Expected on of {operators}.")
        if field and field_value:
            raise TypeError("Expected field name or field value but not both.")
        if reference_field and reference_value:
            raise TypeError(
                "Expected reference field name or reference field value but not both."
            )
        reference_value = reference_value or self._get_as_date(
            reference_field or "report_datetime"
        )
        field_value = field_value or self._get_as_date(field)
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
            value = field_value <= reference_value
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
        if isinstance(value, (str,)):
            value = estimated_date_from_ago(
                cleaned_data=self.cleaned_data, ago_field=key_or_value
            )
        if value:
            try:
                value.date()
            except AttributeError:
                pass
            else:
                value = to_local(value).date()
        return value

    def date_is_after_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        reference_value: datetime | date | None = None,
        inclusive: bool = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is not future to reference_field."""

        msg = msg or self.get_msg(
            "after",
            reference_value=reference_value,
            reference_field=reference_field,
            extra_msg=extra_msg,
            inclusive=inclusive,
        )
        self._date_is(
            GTE if inclusive else GT,
            field=field,
            reference_field=reference_field,
            field_value=field_value,
            reference_value=reference_value,
            msg=msg,
        )

    def date_is_before_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        reference_value: datetime | date | None = None,
        inclusive: bool = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is not before the reference_field."""
        msg = msg or self.get_msg(
            "before",
            reference_value=reference_value,
            reference_field=reference_field,
            extra_msg=extra_msg,
            inclusive=inclusive,
        )
        self._date_is(
            LTE if inclusive else LT,
            field=field,
            reference_field=reference_field,
            field_value=field_value,
            reference_value=reference_value,
            msg=msg,
        )

    @staticmethod
    def get_msg(
        word: str,
        reference_value: date | datetime | None = None,
        reference_field: str | None = None,
        extra_msg: str | None = None,
        inclusive: bool | None = None,
    ) -> str:
        formatted_reference = (
            reference_value.strftime(convert_php_dateformat(settings.DATE_FORMAT))
            if reference_value
            else None
        )
        if inclusive:
            phrase = f"Expected a date on or {word}"
        else:
            phrase = f"Expected a date {word}"
        return (
            f"Invalid. {phrase} `{formatted_reference or reference_field}`. "
            f"{extra_msg or ''}".strip()
        )

    def date_is_equal_or_raise(
        self,
        field=None,
        reference_field=None,
        field_value: datetime | date | None = None,
        reference_value: datetime | date | None = None,
        msg=None,
        extra_msg=None,
    ):
        """Raises if date/datetime field is not equal the reference_field."""
        msg = msg or f"Invalid. Expected dates to match. {extra_msg or ''}".strip()
        self._date_is(
            EQ,
            field=field,
            reference_field=reference_field,
            field_value=field_value,
            reference_value=reference_value,
            msg=msg,
        )

    def date_before_report_datetime_or_raise(
        self,
        field=None,
        report_datetime_field=None,
        inclusive: bool = None,
    ):
        """Convenience method if comparing with report_datetime."""
        msg = None
        report_datetime_field = report_datetime_field or "report_datetime"
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            phrase = "Must be on or" if inclusive else "Must be"
            msg = f"Invalid. {phrase} before report date/time. Got {dte}"
        return self.date_is_before_or_raise(
            field=field,
            reference_field=report_datetime_field,
            inclusive=inclusive,
            msg=msg,
        )

    def date_after_report_datetime_or_raise(
        self,
        field=None,
        report_datetime_field=None,
        inclusive: bool = None,
    ):
        """Convenience method if comparing with report_datetime."""
        msg = None
        report_datetime_field = report_datetime_field or "report_datetime"
        if self.cleaned_data.get(field) and self.cleaned_data.get(report_datetime_field):
            dte = self.cleaned_data.get(report_datetime_field).strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            phrase = "Must be on or" if inclusive else "Must be"
            msg = f"Invalid. {phrase} after report date/time. Got {dte}"
        return self.date_is_after_or_raise(
            field=field,
            reference_field=report_datetime_field,
            inclusive=inclusive,
            msg=msg,
        )
