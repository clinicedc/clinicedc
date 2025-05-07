from __future__ import annotations

import re
from dataclasses import KW_ONLY, dataclass, field

from edc_constants.constants import FEMALE, MALE

from .adult_age_options import adult_age_options

__all__ = ["Formula", "formula", "dummy_formula", "FormulaError"]

from .exceptions import FormulaError


def clean_and_validate_phrase(phrase) -> str:
    phrase_pattern = (
        r"^(([\d+\.]*\d+)?\*?(LLN|ULN)?(<|<=)?(?!\s*=\s*))+x(?!\s*=\s*)"
        r"((<|<=)?([\d+\.]*\d+)?\*?(LLN|ULN)?)?$"
    )
    phrase = phrase.replace(" ", "")
    if not re.match(phrase_pattern, phrase):
        raise FormulaError(
            f"Invalid. Got {phrase}. Expected, e.g, 11<x<22, "
            "11<=x<22, 11<x<=22, 11<x, 11<=x, x<22, x<=22, etc."
        )
    return phrase


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
    lower_inclusive: bool = field(default=False)
    upper_inclusive: bool = field(default=False)
    age_lower_inclusive: bool | None = None
    age_upper_inclusive: bool | None = None
    grade: str | None = None
    lln: str | None = field(default=None, init=False, repr=False)
    uln: str | None = field(default=None, init=False, repr=False)
    lower_operator: str = field(default="", init=False, repr=False)
    upper_operator: str = field(default="", init=False, repr=False)
    age_lower_operator: str = field(default="", init=False, repr=False)
    age_upper_operator: str = field(default="", init=False, repr=False)

    def __post_init__(self):
        self.phrase = clean_and_validate_phrase(self.phrase)
        lower_str, upper_str = self.phrase.split("x")
        for label, _str in {"lower": lower_str, "upper": upper_str}.items():
            if "*" in _str and "LLN" not in _str and "ULN" not in _str:
                raise FormulaError(
                    f"Invalid {label} limit normal in formula. Expected one of LLN or ULN. "
                    f"Got `{self.phrase}`"
                )
        self.lower, self.lower_inclusive, self.lln = self.parse_fragment(lower_str)
        self.upper, self.upper_inclusive, self.uln = self.parse_fragment(upper_str)
        self.gender = [self.gender] if isinstance(self.gender, str) else self.gender
        self.lower_operator = "" if not self.lower else "<=" if self.lower_inclusive else "<"
        self.upper_operator = "" if not self.upper else "<=" if self.upper_inclusive else "<"
        self.age_lower_operator = (
            "" if not self.age_lower else "<=" if self.age_lower_inclusive else "<"
        )
        self.age_upper_operator = (
            "" if not self.age_upper else "<=" if self.age_upper_inclusive else "<"
        )

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
            f"{self.lower or ''}{self.lower_operator}x{self.upper_operator}{self.upper or ''} "
            f"{fasting_str}{','.join(self.gender)} {self.age_description}".rstrip()
        )

    @property
    def age_description(self) -> str:
        return (
            ""
            if not self.age_lower and not self.age_upper
            else (
                f"{self.age_lower or ''}{self.age_lower_operator}"
                f"AGE{self.age_upper_operator}{self.age_upper or ''}"
            )
        )

    @staticmethod
    def parse_fragment(fragment: str) -> tuple[float, bool, str | None]:
        limit_normal: str | None = None
        inclusive = True if "=" in fragment else False
        try:
            value = float(
                fragment.replace("<", "")
                .replace("=", "")
                .replace("*LLN", "")
                .replace("*ULN", "")
            )
        except ValueError:
            value = None
        if "*LLN" in fragment:
            limit_normal = "*LLN"
        elif "*ULN" in fragment:
            limit_normal = "*ULN"
        return value, inclusive, limit_normal

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
