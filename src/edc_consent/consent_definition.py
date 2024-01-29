from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_constants.constants import FEMALE, MALE
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites import site_sites
from edc_utils import floor_secs, formatted_date, formatted_datetime
from edc_utils.date import ceil_datetime, floor_datetime, to_local, to_utc

from .exceptions import (
    ConsentDefinitionError,
    ConsentDefinitionValidityPeriodError,
    ConsentVersionSequenceError,
    NotConsentedError,
)

if TYPE_CHECKING:
    from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin

    from .model_mixins import ConsentModelMixin

    class ConsentLikeModel(NonUniqueSubjectIdentifierModelMixin, ConsentModelMixin):
        ...


@dataclass(order=True)
class ConsentDefinition:
    """A class that represents the general attributes
    of a consent.
    """

    model: str = field(compare=False)
    _ = KW_ONLY
    start: datetime = field(
        default=ResearchProtocolConfig().study_open_datetime, compare=False
    )
    end: datetime = field(default=ResearchProtocolConfig().study_close_datetime, compare=False)
    age_min: int = field(default=18, compare=False)
    age_max: int = field(default=110, compare=False)
    age_is_adult: int = field(default=18, compare=False)
    version: str = field(default="1", compare=False)
    gender: list[str] | None = field(default_factory=list, compare=False)
    updates_versions: list[str] | None = field(default_factory=list, compare=False)
    subject_type: str = field(default="subject", compare=False)
    site_ids: list[int] = field(default_factory=list, compare=False)
    country: str | None = field(default=None, compare=False)
    name: str = field(init=False, compare=True)
    sort_index: str = field(init=False)

    def __post_init__(self):
        self.name = f"{self.model}-{self.version}"
        self.sort_index = self.name
        self.gender = [MALE, FEMALE] if not self.gender else self.gender
        if MALE not in self.gender and FEMALE not in self.gender:
            raise ConsentDefinitionError(f"Invalid gender. Got {self.gender}.")
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if not self.end.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed Got {self.end}.")
        self.check_date_within_study_period()

    @property
    def sites(self):
        if not site_sites.loaded:
            raise ConsentDefinitionError(
                "No registered sites found or edc_sites.sites not loaded yet. "
                "Perhaps place `edc_sites` before `edc_consent` "
                "in INSTALLED_APPS."
            )
        if self.country:
            sites = site_sites.get_by_country(self.country, aslist=True)
        elif self.site_ids:
            sites = [s for s in site_sites.all(aslist=True) if s.site_id in self.site_ids]
        else:
            sites = [s for s in site_sites.all(aslist=True)]
        return sites

    def get_consent_for(
        self,
        subject_identifier: str = None,
        report_datetime: datetime | None = None,
        raise_if_does_not_exist: bool | None = None,
    ) -> ConsentLikeModel | None:
        consent = None
        raise_if_does_not_exist = (
            True if raise_if_does_not_exist is None else raise_if_does_not_exist
        )
        opts: dict[str, str | datetime] = dict(
            subject_identifier=subject_identifier,
            version=self.version,
        )
        if report_datetime:
            opts.update(consent_datetime__lte=to_utc(report_datetime))
        try:
            consent = self.model_cls.objects.get(**opts)
        except ObjectDoesNotExist:
            if raise_if_does_not_exist:
                dte = formatted_date(report_datetime)
                raise NotConsentedError(
                    f"Consent not found. Has subject '{subject_identifier}' "
                    f"completed version '{self.version}' of consent "
                    f"'{self.model_cls._meta.verbose_name}' on or after '{dte}'?"
                )
        return consent

    @property
    def model_cls(self) -> Type[ConsentLikeModel]:
        return django_apps.get_model(self.model)

    @property
    def display_name(self) -> str:
        return (
            f"{self.model_cls._meta.verbose_name} v{self.version} valid "
            f"from {formatted_date(to_local(self.start))} to "
            f"{formatted_date(to_local(self.end))}"
        )

    def valid_for_datetime_or_raise(self, report_datetime: datetime) -> None:
        if not (
            floor_secs(floor_datetime(self.start))
            <= floor_secs(floor_datetime(report_datetime))
            <= floor_secs(floor_datetime(self.end))
        ):
            date_string = formatted_date(report_datetime)
            raise ConsentDefinitionValidityPeriodError(
                "Date does not fall within the validity period."
                f"See {self.name}. Got {date_string}. "
            )

    def check_date_within_study_period(self) -> None:
        """Raises if the date is not within the opening and closing
        dates of the protocol.
        """
        protocol = ResearchProtocolConfig()
        study_open_datetime = protocol.study_open_datetime
        study_close_datetime = protocol.study_close_datetime
        for index, attr in enumerate(["start", "end"]):
            if not (
                floor_secs(floor_datetime(study_open_datetime))
                <= floor_secs(floor_datetime(getattr(self, attr)))
                <= floor_secs(ceil_datetime(study_close_datetime))
            ):
                date_string = formatted_datetime(getattr(self, attr))
                raise ConsentDefinitionError(
                    f"Invalid {attr} date. Cannot be before study start date. "
                    f"See {self}. Got {date_string}."
                )

    def update_previous_consent(self, obj: ConsentLikeModel) -> None:
        if self.updates_versions:
            previous_consent = self.get_previous_consent(
                subject_identifier=obj.subject_identifier,
            )
            previous_consent.subject_identifier_as_pk = obj.subject_identifier_as_pk
            previous_consent.subject_identifier_aka = obj.subject_identifier_aka
            previous_consent.save(
                update_fields=["subject_identifier_as_pk", "subject_identifier_aka"]
            )

    def get_previous_consent(
        self, subject_identifier: str, version: str = None
    ) -> ConsentLikeModel | None:
        """Returns the previous consent or raises if it does
        not exist or is out of sequence with the current.
        """
        if version in self.updates_versions:
            raise ConsentVersionSequenceError(f"Invalid consent version. Got {version}.")
        opts = dict(
            subject_identifier=subject_identifier,
            model_name=self.model,
            version__in=self.updates_versions,
        )
        opts = {k: v for k, v in opts.items() if v is not None}
        try:
            previous_consent = self.model_cls.objects.get(**opts)
        except ObjectDoesNotExist:
            if not self.updates_versions:
                previous_consent = None
            else:
                updates_versions = ", ".join(self.updates_versions)
                raise ConsentVersionSequenceError(
                    f"Failed to update previous version. A previous consent "
                    f"with version in {updates_versions} for {subject_identifier} "
                    f"was not found. Consent version '{self.version}' is "
                    f"configured to update a previous version. "
                    f"See consent definition `{self.name}`."
                )
        except MultipleObjectsReturned:
            previous_consent = self.model_cls.objects.filter(**opts).order_by("-version")[0]
        return previous_consent
