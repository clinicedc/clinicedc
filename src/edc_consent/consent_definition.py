from __future__ import annotations

from datetime import datetime
from reprlib import recursive_repr
from typing import TYPE_CHECKING

from clinicedc_constants import FEMALE, MALE
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_screening.utils import get_subject_screening_model
from edc_sites import site_sites
from edc_utils import ceil_secs, floor_secs, formatted_datetime
from edc_utils.date import to_local

from .exceptions import (
    ConsentDefinitionError,
    ConsentDefinitionValidityPeriodError,
    NotConsentedError,
)

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel
    from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin

    from .consent_definition_extension import ConsentDefinitionExtension
    from .stubs import ConsentLikeModel

    class SubjectScreening(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel): ...


class ConsentDefinition:
    """A class that represents the general attributes
    of a consent.
    """

    def __init__(
        self,
        proxy_model: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        version: str | None = None,
        updates: ConsentDefinition | None = None,
        extends: ConsentDefinition | None = None,
        screening_model: list[str] | None = None,
        age_min: int | None = None,
        age_max: int | None = None,
        age_is_adult: int | None = None,
        gender: list[str] | None = None,
        site_ids: list[int] | None = None,
        country: str | None = None,
        validate_duration_overlap_by_model: bool | None = None,
        subject_type: str | None = None,
        timepoints: list[int] | None = None,
    ) -> None:

        self._model: str | None = None

        # set updated_by when the cdef is registered, see site_consents
        self.updated_by: ConsentDefinition | None = None
        self.extended_by: ConsentDefinitionExtension | None = None

        self.proxy_model = proxy_model
        self.start = start or ResearchProtocolConfig().study_open_datetime
        self.end: datetime = end or ResearchProtocolConfig().study_close_datetime
        self.version = version or "1"
        self.updates = updates
        self.extends = extends
        self.screening_model = screening_model or []

        self.age_min = 18 if age_min is None else age_min
        self.age_max = 110 if age_max is None else age_max
        self.age_is_adult = 18 if age_is_adult is None else age_is_adult
        self.gender = gender or [MALE, FEMALE]

        self.site_ids = site_ids or []
        self.country = country
        self.validate_duration_overlap_by_model = (
            True
            if validate_duration_overlap_by_model is None
            else validate_duration_overlap_by_model
        )
        self.subject_type = subject_type or "subject"
        self.timepoints = timepoints or []

        self.name = f"{self.proxy_model}-{self.version}"
        self.model = self.proxy_model

        if not self.screening_model:
            self.screening_model = [get_subject_screening_model()]
        if MALE not in self.gender and FEMALE not in self.gender:
            raise ConsentDefinitionError(f"Invalid gender. Got {self.gender}.")
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if not self.end.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.end}.")
        self.check_date_within_study_period()

    def _cmp_values(self) -> tuple[datetime, str]:
        """Returns the values used by the comparison methods."""
        return self.start, self.name

    @recursive_repr()
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"proxy_model={self.proxy_model!r}, "
            f"start={self.start!r}, "
            f"end={self.end!r}, "
            f"version={self.version!r}, "
            f"updates={self.updates!r}, "
            f"extends={self.extends!r}, "
            f"screening_model={self.screening_model!r}, "
            f"age_min={self.age_min!r}, "
            f"age_max={self.age_max!r}, "
            f"age_is_adult={self.age_is_adult!r}, "
            f"gender={self.gender!r}, "
            f"site_ids={self.site_ids!r}, "
            f"country={self.country!r}, "
            f"validate_duration_overlap_by_model="
            f"{self.validate_duration_overlap_by_model!r}, "
            f"subject_type={self.subject_type!r}, "
            f"timepoints={self.timepoints!r}, "
            f"name={self.name!r}, "
            f"updated_by={self.updated_by!r}, "
            f"extended_by={self.extended_by!r}, "
            f"_model={self._model!r}, "
        )

    def __eq__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return self._cmp_values() == other._cmp_values()
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return self._cmp_values() < other._cmp_values()
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return self._cmp_values() <= other._cmp_values()
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return self._cmp_values() > other._cmp_values()
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return self._cmp_values() >= other._cmp_values()
        return NotImplemented

    __hash__ = None

    def model_create(self, **kwargs) -> ConsentLikeModel:
        """Creates a consent model instance and inserts version."""
        kwargs.update(version=self.version)
        return self.model_cls.objects.create(**kwargs)

    @property
    def model(self):
        from .managers import (  # noqa: PLC0415
            ConsentObjectsByCdefManager,
            CurrentSiteByCdefManager,
        )

        model_cls = django_apps.get_model(self._model)
        if not model_cls._meta.proxy:
            raise ConsentDefinitionError(
                f"Model class must be a proxy. See {self.name}. Got {model_cls}"
            )
        if not isinstance(model_cls.objects, (ConsentObjectsByCdefManager,)):
            raise ConsentDefinitionError(
                "Incorrect 'objects' model manager for consent model. "
                f"Expected {ConsentObjectsByCdefManager}. See {self.name}.  "
                f"Got {model_cls.objects.__class__}"
            )
        if not isinstance(model_cls.on_site, (CurrentSiteByCdefManager,)):
            raise ConsentDefinitionError(
                "Incorrect 'on_site' model manager for consent model. "
                f"Expected {CurrentSiteByCdefManager}. See {self.name}.  "
                f"Got {model_cls.objects.__class__}"
            )
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
        subject_identifier: str,
        site_id: int | None = None,
        raise_if_not_consented: bool | None = None,
    ) -> ConsentLikeModel | None:
        raise_if_not_consented = (
            True if raise_if_not_consented is None else raise_if_not_consented
        )
        opts: dict[str, str | int] = dict(
            subject_identifier=subject_identifier, version=self.version
        )
        if site_id:
            opts.update(site_id=site_id)
        try:
            consent_obj = self.model_cls.objects.get(**opts)
        except ObjectDoesNotExist:
            consent_obj = None
        if not consent_obj and raise_if_not_consented:
            raise NotConsentedError(
                f"Consent not found for this version. Has subject '{subject_identifier}' "
                f"completed a version '{self.version}' consent?"
            )
        return consent_obj

    @property
    def model_cls(self) -> type[ConsentLikeModel]:
        return django_apps.get_model(self.model)

    @property
    def display_name(self) -> str:
        return (
            f"{self.model_cls._meta.verbose_name} v{self.version} valid "
            f"from {formatted_datetime(to_local(self.start))} to "
            f"{formatted_datetime(to_local(self.end))} ({settings.TIME_ZONE})"
        )

    @property
    def verbose_name(self) -> str:
        return self.model_cls._meta.verbose_name

    def valid_for_datetime_or_raise(self, report_datetime: datetime) -> None:
        if report_datetime and not (
            floor_secs(self.start) <= report_datetime <= ceil_secs(self.end)
        ):
            date_string = formatted_datetime(report_datetime)
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
        for attr in ["start", "end"]:
            if not (
                floor_secs(study_open_datetime)
                <= getattr(self, attr)
                <= ceil_secs(study_close_datetime)
            ):
                open_date_string = formatted_datetime(to_local(study_open_datetime))
                close_date_string = formatted_datetime(to_local(study_close_datetime))
                attr_date_string = formatted_datetime(to_local(getattr(self, attr)))
                raise ConsentDefinitionError(
                    f"Invalid {attr} date. "
                    f"Must be within the opening and closing dates of the protocol. "
                    f"See {self}. "
                    f"Got {open_date_string=}, {close_date_string=}, "
                    f"{attr=}, {attr_date_string=}."
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
        raise ObjectDoesNotExist("Previous consent does not exist")
