from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import FEMALE, MALE
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_screening.utils import get_subject_screening_model
from edc_sites import site_sites
from edc_utils import floor_secs, formatted_date, formatted_datetime
from edc_utils.date import ceil_datetime, floor_datetime, to_local, to_utc

from .exceptions import (
    ConsentDefinitionError,
    ConsentDefinitionValidityPeriodError,
    NotConsentedError,
)

if TYPE_CHECKING:
    from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
    from edc_model.models import BaseUuidModel
    from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin

    from .model_mixins import ConsentModelMixin

    class ConsentLikeModel(NonUniqueSubjectIdentifierModelMixin, ConsentModelMixin): ...

    class SubjectScreening(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel): ...


@dataclass(order=True)
class ConsentDefinition:
    """A class that represents the general attributes
    of a consent.
    """

    proxy_model: str = field(compare=False)
    _ = KW_ONLY
    start: datetime = field(default=ResearchProtocolConfig().study_open_datetime, compare=True)
    end: datetime = field(default=ResearchProtocolConfig().study_close_datetime, compare=False)
    version: str = field(default="1", compare=False)
    updates: tuple[ConsentDefinition, str] = field(default=tuple, compare=False)
    updated_by: str = field(default=None, compare=False)
    screening_model: str = field(default=None, compare=False)
    age_min: int = field(default=18, compare=False)
    age_max: int = field(default=110, compare=False)
    age_is_adult: int = field(default=18, compare=False)
    gender: list[str] | None = field(default_factory=list, compare=False)
    site_ids: list[int] = field(default_factory=list, compare=False)
    country: str | None = field(default=None, compare=False)
    validate_duration_overlap_by_model: bool | None = field(default=True, compare=False)
    subject_type: str = field(default="subject", compare=False)
    name: str = field(init=False, compare=False)
    update_cdef: ConsentDefinition = field(default=None, init=False, compare=False)
    update_model: str = field(default=None, init=False, compare=False)
    update_version: str = field(default=None, init=False, compare=False)
    _model: str = field(init=False, compare=False)
    sort_index: str = field(init=False)

    def __post_init__(self):
        self.model = self.proxy_model
        self.name = f"{self.proxy_model}-{self.version}"
        self.sort_index = self.name
        self.gender = [MALE, FEMALE] if not self.gender else self.gender
        try:
            self.update_cdef, self.update_model = self.updates
        except (ValueError, TypeError):
            pass
        else:
            self.update_version = self.update_cdef.version
        if not self.screening_model:
            self.screening_model = get_subject_screening_model()
        if MALE not in self.gender and FEMALE not in self.gender:
            raise ConsentDefinitionError(f"Invalid gender. Got {self.gender}.")
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if not self.end.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed Got {self.end}.")
        self.check_date_within_study_period()

    @property
    def model(self):
        model_cls = django_apps.get_model(self._model)
        if not model_cls._meta.proxy:
            raise ConsentDefinitionError(f"Model class must be a proxy. Got {model_cls}")
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

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
        raise_if_not_consented: bool | None = None,
    ) -> ConsentLikeModel | None:
        """Returns a subject consent using this consent_definition's
        model_cls and version.

        If it does not exist and this consent_definition updates a
        previous (update_cdef), will try again with the update_cdef's
        model_cls and version.

        Finally, if the subject cosent does not exist raises a
        NotConsentedError.
        """
        consent_obj = None
        raise_if_not_consented = (
            True if raise_if_not_consented is None else raise_if_not_consented
        )
        opts: dict[str, str | datetime] = dict(
            subject_identifier=subject_identifier, version=self.version
        )
        if report_datetime:
            opts.update(consent_datetime__lte=to_utc(report_datetime))
        try:
            consent_obj = self.model_cls.objects.get(**opts)
        except ObjectDoesNotExist:
            if self.update_cdef:
                opts.update(version=self.update_cdef.version)
                try:
                    consent_obj = self.update_cdef.model_cls.objects.get(**opts)
                except ObjectDoesNotExist:
                    pass
        if not consent_obj and raise_if_not_consented:
            dte = formatted_date(report_datetime)
            raise NotConsentedError(
                f"Consent not found. Has subject '{subject_identifier}' "
                f"completed version '{self.version}' of consent on or after '{dte}'?"
            )
        return consent_obj

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

    @property
    def verbose_name(self) -> str:
        return self.model_cls._meta.verbose_name

    def valid_for_datetime_or_raise(self, report_datetime: datetime) -> None:
        if report_datetime and not (
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

    def get_previous_consent(
        self, subject_identifier: str, exclude_id=None
    ) -> ConsentLikeModel:
        previous_consent = (
            self.model_cls.objects.filter(subject_identifier=subject_identifier)
            .exclude(id=exclude_id)
            .order_by("consent_datetime")
        )
        if previous_consent.count() > 0:
            return previous_consent.last()
        else:
            raise ObjectDoesNotExist("Previous consent does not exist")
