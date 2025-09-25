import re
from datetime import date, datetime

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from edc_utils import age

from ..exceptions import ValueBoundryError
from ..formula import clean_and_validate_phrase
from .reference_range_collection import ReferenceRangeCollection

MAX_AGE = 130.0


class ReferenceModelMixin(models.Model):
    reference_range_collection = models.ForeignKey(
        ReferenceRangeCollection, on_delete=models.PROTECT
    )

    label = models.CharField(max_length=25)

    description = models.CharField(max_length=255, default="")

    reference_group = models.CharField(max_length=25, default="")

    lower = models.FloatField(null=True)
    lower_operator = models.CharField(max_length=15, default="")
    lower_inclusive = models.BooleanField(default=False)
    lln = models.CharField(max_length=15, default="")

    upper = models.FloatField(null=True)
    upper_operator = models.CharField(max_length=2, default="")
    upper_inclusive = models.BooleanField(default=False)
    uln = models.CharField(max_length=15, default="")

    gender = models.CharField(max_length=1, validators=[RegexValidator(r"[MF]{1}")])
    units = models.CharField(max_length=15)

    age_units = models.CharField(max_length=15)

    age_lower = models.IntegerField()
    age_lower_operator = models.CharField(max_length=15)
    age_lower_inclusive = models.BooleanField(default=False)

    age_upper = models.IntegerField(null=True)
    age_upper_operator = models.CharField(max_length=15, default="")
    age_upper_inclusive = models.BooleanField(null=True)

    fasting = models.BooleanField(default=False)

    phrase = models.CharField(
        max_length=50,
        default="",
        verbose_name="Value phrase",
        help_text="calculated by the formula instance",
    )

    age_phrase = models.CharField(max_length=25, default="", help_text="calculated in save()")

    grade = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def save(self, *args, **kwargs):
        self.age_phrase = (
            f"{self.age_lower or ''}{self.age_lower_operator or ''}"
            f"%(age_value)s{self.age_upper_operator or ''}{self.age_upper or ''}"
        )
        self.phrase = self.get_phrase()
        self.description = self.get_description()
        super().save(*args, **kwargs)

    def get_phrase(self) -> str:
        lower = self.lower or ""
        upper = self.upper or ""
        phrase = (
            f"{lower}{self.lln or ''}{self.lower_operator or ''}x"
            f"{self.upper_operator or ''}{upper}{self.uln or ''}"
        )
        clean_and_validate_phrase(phrase)
        return phrase

    def get_description(self, exclude_label: bool | None = None) -> str:
        age_description = (
            ""
            if not self.age_lower and not self.age_upper
            else (
                f"{self.age_lower or ''}{self.age_lower_operator}"
                f"AGE{self.age_upper_operator}{self.age_upper or ''}"
            )
        )
        try:
            fasting = self.fasting
        except KeyError:
            fasting_str = ""
        else:
            fasting_str: str = "Fasting " if fasting else ""
        label = "" if exclude_label else f"{self.label}: "
        grade = ""
        if self.grade is not None:
            grade = f"GRADE{self.grade} "
        return (
            f"{label}"
            f"{self.phrase} "
            f"{self.units} {fasting_str}{grade}{self.gender} "
            f"{age_description}".rstrip()
        )

    def age_in_bounds_or_raise(
        self, dob: date, report_datetime: datetime, age_units: str | None = None
    ) -> bool:
        pattern = r"([<>]=?|==|!=)?\s*-?\d+(\.\d+)?"
        age_units = age_units or "years"
        if age_units not in ["days", "months", "years"]:
            raise ValueError(
                f"Invalid age units. Expected one of {['days', 'months', 'years']}. "
                f"Got {age_units}"
            )
        rdelta = age(dob, report_datetime)
        age_value = getattr(rdelta, age_units)
        if not isinstance(age_value, (int, float)) or not (0.0 <= age_value <= MAX_AGE):
            raise ValueError(f"Invalid age value. Got {age_value}.")
        age_condition_str = self.age_phrase % dict(age_value=age_value)
        if not re.match(pattern, age_condition_str):
            raise ValueError(f"Invalid age condition string. Got {age_condition_str}.")
        if not eval(age_condition_str):  # noqa: S307
            raise ValueBoundryError(
                f"Age is out of bounds. See {self}. Got AGE={age_value} {age_units}."
            )
        return True

    class Meta:
        abstract = True
