from __future__ import annotations

from datetime import datetime

from django.apps import apps as django_apps
from edc_constants.constants import FEMALE, MALE


class InvalidGender(Exception):
    pass


class NaiveDatetimeError(Exception):
    pass


class Consent:
    default_version = "1"
    default_subject_type = "subject"
    default_consent_group = django_apps.get_app_config("edc_consent").default_consent_group

    def __init__(
        self,
        model: str,
        group: str = None,
        start: datetime = None,
        end: datetime = None,
        version: str | None = None,
        gender: list[str] = None,
        updates_versions: list[str] | str | None = None,
        age_min: int = None,
        age_max: int = None,
        age_is_adult: int | None = None,
        subject_type: str | None = None,
        proxy_models: list[str] | None = None,
    ):
        """A class that represents the general attributes
        of a consent.
        """
        if not start.tzinfo:
            raise NaiveDatetimeError(f"Naive datetime is invalid. Got {start}.")
        if not end.tzinfo:
            raise NaiveDatetimeError(f"Naive datetime is invalid. Got {end}.")
        if MALE not in gender and FEMALE not in gender:
            raise InvalidGender(f"Invalid gender. Got {gender}.")
        self.model = model
        self.proxy_models = proxy_models or []
        self.group = group or self.default_consent_group
        self.start = start
        self.end = end
        self.updates_versions = updates_versions or []
        self.version = version or self.default_version
        self.gender = gender
        self.age_min = age_min
        self.age_max = age_max
        self.age_is_adult = age_is_adult
        self.subject_type = subject_type or self.default_subject_type
        self.verbose_name = f"{self.model} {self.version}"
        self.name = f"{self.model}-{self.version}"
        if self.updates_versions:
            if not isinstance(self.updates_versions, (list, tuple)):
                self.updates_versions = [
                    x.strip() for x in self.updates_versions.split(",") if x.strip() != ""
                ]

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.model}, {self.version}) "
            f"from {self.start} to {self.end}>"
        )

    def __str__(self):
        return self.verbose_name

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)
