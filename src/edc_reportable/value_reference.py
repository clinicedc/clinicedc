from __future__ import annotations

from datetime import date, datetime

from .age_evaluator import AgeEvaluator
from .evaluator import Evaluator, ValueBoundryError


class ValueReference:
    age_evaluator_cls = AgeEvaluator
    evaluator_cls = Evaluator

    def __init__(
        self,
        name: str = None,
        lower: float | None = None,
        upper: float | None = None,
        gender: str | list[str] = None,
        units: str = None,
        **kwargs,
    ):
        self._lower = None
        self._upper = None
        self.name = name
        self.units = units
        self.gender = "".join(gender) if isinstance(gender, (list,)) else gender
        self.lower = lower
        self.upper = upper
        self.evaluator = self.evaluator_cls(
            name=self.name, units=units, lower=self.lower, upper=self.upper, **kwargs
        )
        self.age_evaluator = self.age_evaluator_cls(
            lower=self.lower, upper=self.upper, **kwargs
        )
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.description()})"

    @property
    def lower(self):
        return self._lower

    @lower.setter
    def lower(self, value):
        self._lower = value

    @property
    def upper(self):
        return self._upper

    @upper.setter
    def upper(self, value):
        self._upper = value

    def description(self, **kwargs) -> str:
        return (
            f"{self.evaluator.description(**kwargs)} {self.gender} "
            f"{self.age_evaluator.description()}"
        )

    def key(self, **kwargs) -> str:
        return self.description(**kwargs)

    def in_bounds(self, value: int | float = None, units: str = None) -> bool:
        try:
            in_bounds = self.evaluator.in_bounds_or_raise(value, units=units)
        except ValueBoundryError:
            in_bounds = False
        return in_bounds

    def age_match(
        self, dob: date = None, report_datetime: datetime = None, age_units: str | None = None
    ) -> bool:
        try:
            age_match = self.age_evaluator.in_bounds_or_raise(
                dob=dob, report_datetime=report_datetime, age_units=age_units
            )
        except ValueBoundryError:
            age_match = False
        return age_match
