from __future__ import annotations

import re
from dataclasses import KW_ONLY, dataclass, field

from edc_constants.constants import FEMALE, MALE

from .adult_age_options import adult_age_options
from .constants import LLN, ULN

__all__ = ["Formula", "formula", "dummy_formula"]

from .exceptions import FormulaError


@dataclass()
class Formula:
    phrase: str
    _ = KW_ONLY
    units: str | None = None
    fasting: bool | None = field(default=False)
    gender: str | list[str] = field(default="")
    age_lower: str = field(default="")
    age_upper: str = field(default="")
    age_units: str = field(default="")
    lower_inclusive: bool | None = None
    upper_inclusive: bool | None = None
    age_lower_inclusive: bool | None = None
    age_upper_inclusive: bool | None = None
    grade: str | None = None
    phrase_pattern: str = field(
        default=r"(([\d+\.\d+]|[\.\d+])?(<|<=)?)+x((<|<=)?([\d+\.\d+]|[\.\d+])+)?",
        init=False,
        repr=False,
    )
    lln: str = field(default=f"*{LLN}", init=False, repr=False)
    uln: str = field(default=f"*{ULN}", init=False, repr=False)

    def __post_init__(self):
        self.clean_and_validate_phrase()
        lower_str, upper_str = self.phrase.split("x")
        self.lower, self.lower_inclusive = self.parse_fragment(lower_str)
        self.upper, self.upper_inclusive = self.parse_fragment(upper_str)
        for name, value in {"lower": self.lower, "upper": self.upper}.items():
            if value:
                try:
                    _, label = self.lower.split("*")
                except AttributeError:
                    pass
                else:
                    if label not in ["LLN", "ULN"]:
                        raise FormulaError(
                            "Invalid limit label. Expected one of LLN or ULN. "
                            f"See {name} attr. Got `{label}`"
                        )
        self.gender = [self.gender] if isinstance(self.gender, str) else self.gender

    def __str__(self) -> str:
        return self.description

    @property
    def description(self) -> str:
        try:
            fasting = self.fasting
        except KeyError:
            fasting_str = ""
        else:
            fasting_str: str = "Fasting " if fasting else ""
        return (
            f"{self.lower}{self.lower_op}x{self.upper_op}{self.upper} "
            f"{fasting_str}{','.join(self.gender)} {self.age}".rstrip()
        )

    def clean_and_validate_phrase(self) -> None:
        self.phrase = self.phrase.replace(" ", "")
        match = re.match(
            self.phrase_pattern, self.phrase.replace(self.lln, "").replace(self.uln, "")
        )
        if not match or match.group() != self.phrase.replace(self.lln, "").replace(
            self.uln, ""
        ):
            raise FormulaError(
                f"Invalid. Got {self.phrase}. Expected, e.g, 11<x<22, "
                "11<=x<22, 11<x<=22, 11<x, 11<=x, x<22, x<=22, etc."
            )

    @property
    def lower_op(self) -> str:
        return "" if not self.lower else "<=" if self.lower_inclusive else "<"

    @property
    def upper_op(self) -> str:
        return "" if not self.upper else "<=" if self.upper_inclusive else "<"

    @property
    def age_lower_op(self) -> str:
        return "" if not self.age_lower else "<=" if self.age_lower_inclusive else "<"

    @property
    def age_upper_op(self) -> str:
        return "" if not self.age_upper else "<=" if self.age_upper_inclusive else "<"

    @property
    def age(self) -> str:
        return (
            ""
            if not self.age_lower and not self.age_upper
            else f"{self.age_lower}{self.age_lower_op}AGE{self.age_upper_op}{self.age_upper}"
        )

    def parse_fragment(self, fragment: str) -> tuple[str, bool | None]:
        inclusive = True if "=" in fragment else None
        try:
            value = float(
                fragment.replace("<", "")
                .replace("=", "")
                .replace(self.lln, "")
                .replace(self.uln, "")
            )
        except ValueError:
            value = None
        if self.lln in fragment:
            value = f"{value}{self.lln}"
        elif self.uln in fragment:
            value = f"{value}{self.uln}"
        return value, inclusive

    # def parse(
    #     uln: str | None = None,
    #     lln: str | None = None,
    #     **kwargs,
    # ) -> Formula:
    #     pattern: str = r"(([\d+\.\d+]|[\.\d+])?(<|<=)?)+x((<|<=)?([\d+\.\d+]|[\.\d+])+)?"
    #     lln: str = f"*{LLN}"
    #     uln: str = f"*{ULN}"
    #
    #     def _parse(string: str) -> tuple[str, bool | None]:
    #         inclusive = True if "=" in string else None
    #         try:
    #             value = float(
    #               string.replace("<", "").replace("=", "").replace(lln, "").replace(uln, "")
    #             )
    #         except ValueError:
    #             value = None
    #         if lln in string:
    #             value = f"{value}{lln}"
    #         elif uln in string:
    #             value = f"{value}{uln}"
    #         return value, inclusive
    #
    #     phrase = phrase.replace(" ", "")
    #     match = re.match(pattern, phrase.replace(lln, "").replace(uln, ""))
    #     if not match or match.group() != phrase.replace(lln, "").replace(uln, ""):
    #         raise ParserError(
    #             f"Invalid. Got {phrase}. Expected, e.g, 11<x<22, "
    #             "11<=x<22, 11<x<=22, 11<x, 11<=x, x<22, x<=22, etc."
    #         )
    #     left, right = phrase.replace(" ", "").split("x")
    #     lower, lower_inclusive = _parse(left)
    #     upper, upper_inclusive = _parse(right)
    #     fasting = True if fasting else False
    #     formula = Formula(
    #         lower=lower,
    #         lower_inclusive=lower_inclusive,
    #         upper=upper,
    #         upper_inclusive=upper_inclusive,
    #         fasting=fasting,
    #         **kwargs,
    #     )
    #     return formula


def formula(*args, **kwargs):
    return Formula(*args, **kwargs).description


def dummy_formula(phrase: str = None, units: str = None) -> Formula:
    return Formula(
        phrase or "0<=x",
        units=units,
        gender=[MALE, FEMALE],
        **adult_age_options,
    )
