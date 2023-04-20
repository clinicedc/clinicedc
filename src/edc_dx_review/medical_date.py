from __future__ import annotations

from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from edc_constants.constants import GT, GTE, LT, LTE
from edc_model import estimated_date_from_ago
from edc_utils import convert_php_dateformat

FAILED_COMPARISON = "FAILED_COMPARISON"
BEFORE_AFTER_BOTH_TRUE = "BEFORE_AFTER_BOTH_TRUE"
BEFORE_AFTER_BOTH_FALSE = "BEFORE_AFTER_BOTH_FALSE"
MISSING_REPORT_DATETIME = "MISSING_REPORT_DATETIME"
MISSING_DATE_AND_AGO = "MISSING_DATE_AND_AGO"
DATE_AND_AGO_CONFLICT = "DATE_AND_AGO_CONFLICT"


class MedicalDateError(ValidationError):
    def __init__(self, message: dict, code: str = None, params=None):
        self.code = code
        super().__init__(message, code, params)

    @property
    def message_dict(self):
        getattr(self, "error_dict")
        return {k: v[0] for k, v in dict(self).items()}


class MedicalDate(date):
    _after_reference: bool = None
    _before_reference: bool = None
    _cleaned_data: dict = None
    _date_field: str = None
    _ago_field: str = None
    _field: str = None
    _inclusive: bool = None
    _label: str = None
    _op: str = None
    _reference_date: date | datetime | MedicalDate = None
    _value: date = None
    _word: str = None

    def __new__(
        cls,
        date_field: str,
        ago_field: str,
        cleaned_data: dict,
        reference_date: date | datetime | MedicalDate,
        reference_is_none_msg: str,
        before_reference: bool | None = None,
        after_reference: bool | None = None,
        inclusive: bool | None = None,
        label: str | None = None,
    ):
        cls._after_reference = after_reference
        cls._before_reference = before_reference
        cls._cleaned_data = cleaned_data
        cls._date_field = date_field
        cls._ago_field = ago_field
        cls._inclusive = inclusive
        cls._label = label

        cls._report_date_or_raise()
        cls._one_date_or_raise()
        cls._date_or_raise()
        try:
            cls._value = cls._cleaned_data.get(cls._date_field).date()
        except AttributeError:
            cls._value = cls._cleaned_data.get(cls._date_field)
        if cls._value:
            cls._field = cls._date_field
        else:
            cls._field = cls._ago_field
            cls._value = estimated_date_from_ago(
                cleaned_data=cls._cleaned_data, ago_field=cls._ago_field
            )
        try:
            cls._reference_date = reference_date.date()
        except AttributeError:
            cls._reference_date = reference_date
        cls._op, cls._word = cls._get_operator()
        if not cls._compare_date_and_reference():
            cls._raise_on_failed_comparison()
        if (
            cls._cleaned_data.get("report_datetime").date() != cls._reference_date
            and cls._value > cls._cleaned_data.get("report_datetime").date()
        ):
            raise MedicalDateError(
                {cls._field: "Cannot be after report date"},
                code=FAILED_COMPARISON,
            )
        return super().__new__(
            cls, year=cls._value.year, month=cls._value.month, day=cls._value.day
        )

    @classmethod
    def _report_date_or_raise(cls):
        if not cls._cleaned_data.get("report_datetime"):
            raise MedicalDateError(
                {"__all__": "Complete the report date."}, code=MISSING_REPORT_DATETIME
            )

    @classmethod
    def _one_date_or_raise(cls):
        if cls._cleaned_data.get(cls._date_field) and cls._cleaned_data.get(cls._ago_field):
            raise MedicalDateError(
                {
                    cls._ago_field: (
                        "Date conflict. Do not provide a response "
                        f"here if {cls._label} date is available."
                    )
                },
                DATE_AND_AGO_CONFLICT,
            )

    @classmethod
    def _date_or_raise(cls):
        if not cls._cleaned_data.get(cls._date_field) and not cls._cleaned_data.get(
            cls._ago_field
        ):
            raise MedicalDateError(
                {"__all__": f"Complete the {cls._label or '????'} date."},
                code=MISSING_DATE_AND_AGO,
            )

    @classmethod
    def _get_operator(cls):
        msg = f"Is `{cls._field}` supposed to be before or after `{cls._label}` date?"
        if cls._before_reference and cls._after_reference:
            raise MedicalDateError({"__all__": msg}, code=BEFORE_AFTER_BOTH_TRUE)
        if cls._before_reference:
            op = LTE if cls._inclusive else LT
            word = "before"
        elif cls._after_reference:
            op = GTE if cls._inclusive else GT
            word = "after"
        else:
            raise MedicalDateError({"__all__": msg}, code=BEFORE_AFTER_BOTH_FALSE)
        return op, word

    @classmethod
    def _compare_date_and_reference(cls) -> bool:
        value = None
        if cls._op == LT:
            value = cls._value < cls._reference_date
        elif cls._op == LTE:
            value = cls._value <= cls._reference_date
        elif cls._op == GT:
            value = cls._value > cls._reference_date
        elif cls._op == GTE:
            value = cls._value >= cls._reference_date
        return value

    @classmethod
    def _raise_on_failed_comparison(cls):
        formatted_ref = cls._reference_date.strftime(
            convert_php_dateformat(settings.DATE_FORMAT)
        )
        formatted_dte = cls._value.strftime(convert_php_dateformat(settings.DATE_FORMAT))
        inclusive_str = " on or " if cls._inclusive else " "
        raise MedicalDateError(
            {
                cls._field: (
                    f"{cls._label.title()} date must be{inclusive_str}{cls._word} "
                    f"`{formatted_ref}` [{cls._op}]. Got {formatted_dte}"
                )
            },
            code=FAILED_COMPARISON,
        )


class DxDate(MedicalDate):
    def __new__(cls, cleaned_data: dict, **kwargs) -> DxDate:
        defaults = dict(
            before_reference=True,
            reference_date=cleaned_data.get("report_datetime"),
            reference_is_none_msg="Complete the report date first.",
            inclusive=True,
            label="diagnosis",
        )
        defaults.update(**kwargs)
        return super().__new__(cls, "dx_date", "dx_ago", cleaned_data, **defaults)


class RxDate(MedicalDate):
    def __new__(cls, cleaned_data: dict, reference_date: date | DxDate, **kwargs) -> RxDate:
        defaults = dict(
            after_reference=True,
            reference_is_none_msg="Complete the diagnosis date.",
            inclusive=True,
            label="treatment",
        )
        defaults.update(reference_date=reference_date, **kwargs)
        return super().__new__(cls, "rx_init_date", "rx_init_ago", cleaned_data, **defaults)
