import re
from datetime import date, datetime

# from django.contrib.sites.models import Site
# from django.db import models
from edc_model.models import BaseUuidModel

from ..exceptions import ValueBoundryError
from .model_mixins import ReferenceModelMixin


class NormalData(ReferenceModelMixin, BaseUuidModel):

    # sites = models.ManyToManyField(Site, blank=True)

    def __str__(self):
        return self.description

    def value_in_normal_range_or_raise(
        self,
        value: int | float,
        dob: date = None,
        report_datetime: datetime = None,
        age_units: str | None = None,
    ) -> bool:
        """Raises a ValueBoundryError exception if condition not met.

        Condition is evaluated to True or False as a string
        constructed from given parameters.

        For example,
            "lower lower_operator value upper_operator upper"
            "1.7<3.6<=3.5"
            "7.3<3.6"
        """

        pattern = r"([<>]=?|==|!=)?\s*-?\d+(\.\d+)?"

        self.age_in_bounds_or_raise(dob, report_datetime, age_units)

        value = float(value)
        value_condition_str = (
            f'{"" if self.lower is None else self.lower}{self.lower_operator or ""}{value}'
            f'{self.upper_operator or ""}{"" if self.upper is None else self.upper}'
        )
        if not re.match(pattern, value_condition_str):
            raise ValueError(f"Invalid condition string. Got {value_condition_str}.")
        if not eval(value_condition_str):  # nosec B307
            raise ValueBoundryError(
                f"{self.label}: {value_condition_str}{self.units} [{self.gender}]"
            )
        return True

    class Meta:
        verbose_name = "Normal Reference"
        verbose_name_plural = "Normal References"
