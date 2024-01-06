from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from edc_constants.constants import FEMALE, MALE
from edc_protocol import Protocol
from edc_utils import floor_secs, formatted_datetime
from edc_utils.date import ceil_datetime, floor_datetime, to_local, to_utc

from .exceptions import ConsentDefinitionError

if TYPE_CHECKING:
    from .model_mixins import ConsentModelMixin


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
        self.name = f"{self.model}-{self.version}"
        if MALE not in self.gender and FEMALE not in self.gender:
            raise ConsentDefinitionError(f"Invalid gender. Got {self.gender}.")
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if not self.end.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed Got {self.end}.")
        self.check_date_within_study_period()

    def get_consent_for(
        self, subject_identifier: str = None, report_datetime: datetime | None = None
    ) -> ConsentModelMixin:
        opts: dict[str, str | datetime] = dict(
            subject_identifier=subject_identifier,
            version=self.version,
        )
        if report_datetime:
            opts.update(consent_datetime__lte=to_utc(report_datetime))
        return self.model_cls.objects.get(**opts)

    @property
    def model_cls(self) -> Type[ConsentModelMixin]:
        return django_apps.get_model(self.model)

    @property
    def display_name(self) -> str:
        return (
            f"{self.model_cls._meta.verbose_name} v{self.version} valid "
            f"from {formatted_datetime(to_local(self.start))} to "
            f"{formatted_datetime(to_local(self.end))}"
        )

    def check_date_within_study_period(self) -> None:
        """Raises if the date is not within the opening and closing
        dates of the protocol.
        """
        protocol = Protocol()
        study_open_datetime = protocol.study_open_datetime
        study_close_datetime = protocol.study_close_datetime
        for index, attr in enumerate(["start", "end"]):
            if not (
                floor_secs(floor_datetime(study_open_datetime))
                <= floor_secs(getattr(self, attr))
                <= floor_secs(ceil_datetime(study_close_datetime))
            ):
                date_string = formatted_datetime(getattr(self, attr))
                raise ConsentDefinitionError(
                    f"Invalid {attr} date. Cannot be before study start date. "
                    f"See {self}. Got {date_string}."
                )
