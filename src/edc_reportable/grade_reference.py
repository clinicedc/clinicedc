from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .constants import GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5, LLN, ULN
from .exceptions import GradeReferenceError
from .utils import get_normal_reference
from .value_reference import ValueReference

if TYPE_CHECKING:
    from .normal_reference import NormalReference


class GradeReference(ValueReference):
    grades: list[str] = [GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5]

    def __init__(
        self,
        grade: int = None,
        lower: float | str | None = None,
        upper: float | str | None = None,
        normal_references: list[NormalReference] = None,
        **kwargs,
    ):
        self._normal_reference: NormalReference | None = None
        if str(grade) not in self.grades:
            raise GradeReferenceError(
                f"Invalid grade. Expected one of {self.grades}. Got {grade}."
            )
        self.grade = grade
        self.normal_references = normal_references
        super().__init__(lower=lower, upper=upper, **kwargs)

    @property
    def lower(self):
        return self._lower

    @lower.setter
    def lower(self, value):
        self._lower = self.get_value_relative_to_limit_normal(value)

    @property
    def upper(self):
        return self._upper

    @upper.setter
    def upper(self, value):
        self._upper = self.get_value_relative_to_limit_normal(value)

    @property
    def normal_reference(self):
        if not self._normal_reference:
            self._normal_reference = get_normal_reference(
                name=self.name,
                gender=self.gender,
                units=self.units,
                normal_references=self.normal_references,
                exception_cls=GradeReferenceError,
            )
            # normal_reference = [
            #     x
            #     for x in self.normal_references or []
            #     if x.units == self.units
            #     and (
            #         self.gender in x.gender
            #         or self.gender == x.gender
            #         or self.gender in "".join(x.gender)
            #     )
            # ]
            # if not normal_reference:
            #     raise GradeReferenceError(
            #         f"Normal references not found. Need normal reference
            #         for {self.name} {self.units} {self.gender}. Have {
            #         self.normal_references}"
            #     )
            # elif len(normal_reference) > 1:
            #     raise GradeReferenceError(
            #         "Multiple normal references found. "
            #         f"Got {self.name} {self.units} {self.gender}"
            #     )
            # else:
            #     self._normal_reference = normal_reference[0]
        return self._normal_reference

    def description(self, **kwargs):
        return f"{super().description(**kwargs)} GRADE {self.grade}"

    def get_value_relative_to_limit_normal(self, value: str) -> int | float:
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
                raise GradeReferenceError(
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
