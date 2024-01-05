from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime

from django.apps import apps as django_apps
from edc_constants.constants import FEMALE, MALE
from edc_utils import formatted_date


class InvalidGender(Exception):
    pass


class NaiveDatetimeError(Exception):
    pass


@dataclass(order=True)
class ConsentDefinition:
    """A class that represents the general attributes
    of a consent.
    """

    model: str = field(compare=False)
    _ = KW_ONLY
    start: datetime = field(compare=False)
    end: datetime = field(compare=False)
    age_min: int = field(compare=False)
    age_max: int = field(compare=False)
    age_is_adult: int | None = field(compare=False)
    name: str = field(init=False, compare=True)
    version: str = field(default="1", compare=False)
    gender: list[str] = field(default_factory=list, compare=False)
    subject_type: str = field(default="subject", compare=False)
    updates_versions: list[str] = field(default_factory=list, compare=False)
    proxy_models: list[str] = field(default_factory=list, compare=False)

    def __post_init__(self):
        if not self.start.tzinfo:
            raise NaiveDatetimeError(f"Naive datetime is invalid. Got {self.start}.")
        if not self.end.tzinfo:
            raise NaiveDatetimeError(f"Naive datetime is invalid. Got {self.end}.")
        if MALE not in self.gender and FEMALE not in self.gender:
            raise InvalidGender(f"Invalid gender. Got {self.gender}.")
        self.name = f"{self.model}-{self.version}"

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    @property
    def display_name(self) -> str:
        return (
            f"{self.model_cls._meta.verbose_name} v{self.version} valid "
            f"from {formatted_date(self.start)} to {formatted_date(self.end)}"
        )
