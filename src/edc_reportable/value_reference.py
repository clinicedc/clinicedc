from __future__ import annotations

import re
from datetime import date, datetime
from typing import TYPE_CHECKING

from .age_evaluator import AgeEvaluator
from .constants import LLN, ULN
from .evaluator import Evaluator, ValueBoundryError
from .exceptions import ValueReferenceError

if TYPE_CHECKING:
    from .normal_reference import NormalReference


class ValueReference:
    age_evaluator_cls = AgeEvaluator
    evaluator_cls = Evaluator

    def __init__(
        self,
        name: str = None,
        gender: str | list[str] = None,
        units: str = None,
        normal_references: dict[str, NormalReference] = None,
        lower: float | str | None = None,
        upper: float | str | None = None,
        **kwargs,
    ):
        self._normal_reference: NormalReference | None = None
        self.normal_references = normal_references
        self.name = name
        self.units = units
        self.gender = "".join(gender) if isinstance(gender, (list,)) else gender
        self.lower = self.get_boundary_or_boundary_relative_to_limit_normal(lower)
        self.upper = self.get_boundary_or_boundary_relative_to_limit_normal(upper)
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

    def description(self, **kwargs) -> str:
        return (
            f"{self.evaluator.description(**kwargs)} {self.gender} "
            f"{self.age_evaluator.description()}"
        )

    def key(self, **kwargs) -> str:
        return self.description(**kwargs)

    def in_bounds(self, value: int | float = None, **kwargs) -> bool:
        try:
            in_bounds = self.evaluator.in_bounds_or_raise(value, **kwargs)
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

    @property
    def normal_reference(self) -> NormalReference:
        if not self._normal_reference:
            if self.normal_references:
                self._normal_reference = [
                    x[0] for x in self.normal_references.values() if x[0].units == self.units
                ]
            else:
                raise ValueReferenceError(
                    f"Normal references not provided. Got {self.name} per {self.units}"
                )
            if not self._normal_reference:
                opts = [(x[0].name, x[0].units) for x in self.normal_references.values()]
                raise ValueReferenceError(
                    "Normal reference not found. Expected one "
                    f"of {opts}. Got {self.name} per {self.units}"
                )
        return self._normal_reference[0]

    def get_boundary_or_boundary_relative_to_limit_normal(self, value: str) -> int | float:
        """Return either upper or lower boundary value as a literal
        value or as a value relative to the lower limit normal or
        upper limit normal.

        Parameter `value` may be a float, None or a string

        If LLN or ULN, uses normal reference value.
        """
        pattern = rf"(\d+\.\d+)\*({LLN}|{ULN})"
        try:
            value = value.upper()
        except AttributeError:
            pass
        else:
            if not re.match(pattern, value):
                raise ValueReferenceError(
                    f"Invalid value. Unable to parse value string for {LLN} or {ULN}. "
                    f"Got {value}."
                )
            else:
                factor, limit_normal_label = value.split("*")
                if limit_normal_label == LLN:
                    value = float(factor) * self.normal_reference.lower
                elif limit_normal_label == ULN:
                    value = float(factor) * self.normal_reference.upper
        return value
