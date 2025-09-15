from __future__ import annotations

import re

from .constants import HIGH_VALUE
from .exceptions import ValueBoundryError


class InvalidUnits(Exception):
    pass


class InvalidLowerBound(Exception):
    pass


class InvalidLowerLimitNormal(Exception):
    pass


class InvalidUpperLimitNormal(Exception):
    pass


class InvalidUpperBound(Exception):
    pass


class InvalidCombination(Exception):
    pass


class Evaluator:
    def __init__(
        self,
        name: str = None,
        lower: int | float = None,
        upper: int | float = None,
        units: str = None,
        lower_inclusive: bool | None = None,
        upper_inclusive: bool | None = None,
        **kwargs,
    ) -> None:
        self.name = name
        if lower is not None and not re.match(r"\d+", str(lower)):
            raise InvalidLowerBound(f"Got {lower}.")
        if upper is not None and not re.match(r"\d+", str(upper)):
            raise InvalidUpperBound(f"Got {upper}.")
        self.lower: float | None = None if lower is None else float(lower)
        self.upper: float | None = None if upper is None else float(upper)

        if self.lower is not None and self.upper is not None:
            if self.lower == self.upper:
                raise InvalidCombination(
                    f"Lower and upper bound cannot be equal. Got {lower}={upper}"
                )
            if self.lower > self.upper:
                raise InvalidCombination(
                    f"Lower bound cannot exceed upper bound. Got {lower}>{upper}"
                )
        if not units:
            raise InvalidUnits("Got 'units' is None")
        self.units = units
        self.lower_inclusive = lower_inclusive
        self.upper_inclusive = upper_inclusive
        self.lower_operator: str | None = (
            None if self.lower is None else "<=" if self.lower_inclusive is True else "<"
        )
        self.upper_operator: str | None = (
            None if self.upper is None else "<=" if self.upper_inclusive is True else "<"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description()})"

    def __str__(self) -> str:
        return self.description()

    def description(
        self,
        value: int | float = None,
        show_as_int: bool = None,
        placeholder: str | None = None,
    ) -> str:
        placeholder = placeholder or "x"
        if show_as_int:
            value = int(value) if value is not None else placeholder
            lower = int(self.lower) if self.lower is not None else ""
            upper = int(self.upper) if self.upper is not None else ""
        else:
            value = float(value) if value is not None else placeholder
            lower = float(self.lower) if self.lower is not None else ""
            upper = float(self.upper) if self.upper is not None else ""
        if upper and upper >= float(HIGH_VALUE):
            upper = ""
        return (
            f"{lower}{self.lower_operator or ''}{value}"
            f"{self.upper_operator or ''}{upper} {self.units}"
        )

    def in_bounds_or_raise(self, value: int | float, units: str = None) -> bool:
        """Raises a ValueBoundryError exception if condition not met.

        The condition is evaluated to True or False as a string
        constructed from given parameters.

        For example,
            "lower lower_operator value upper_operator upper"
            "1.7<3.6<=3.5"
            "7.3<3.6"
        """
        value = float(value)
        if units != self.units:
            raise InvalidUnits(f"Expected {self.units}. See {self!r}")
        condition_str = (
            f"{'' if self.lower is None else self.lower}{self.lower_operator or ''}{value}"
            f"{self.upper_operator or ''}{'' if self.upper is None else self.upper}"
        )
        if not eval(condition_str):  # nosec B307
            raise ValueBoundryError(condition_str)
        return True
