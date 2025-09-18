from __future__ import annotations

from datetime import date, datetime

from django.utils import timezone

from edc_utils import age

from .evaluator import Evaluator


class AgeEvaluator(Evaluator):
    def __init__(
        self,
        age_lower: int | None = None,
        age_upper: int = None,
        age_units: str | None = None,
        age_lower_inclusive: bool | None = None,
        age_upper_inclusive: bool | None = None,
        **kwargs,
    ):
        kwargs["units"] = age_units or "years"
        kwargs["lower"] = age_lower or 0
        kwargs["upper"] = age_upper
        kwargs["lower_inclusive"] = age_lower_inclusive
        kwargs["upper_inclusive"] = age_upper_inclusive
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description(show_as_int=True)})"

    def description(self, value: int = None, **kwargs):
        kwargs["show_as_int"] = True
        kwargs["placeholder"] = "AGE"
        return super().description(value=value, **kwargs)

    def in_bounds_or_raise(
        self,
        dob: date = None,
        report_datetime: datetime = None,
        age_units: str | None = None,
    ) -> bool:
        report_datetime = report_datetime or timezone.now()
        age_units = age_units or "years"
        rdelta = age(dob, report_datetime)
        value = getattr(rdelta, self.units)
        return super().in_bounds_or_raise(value, units=age_units)
