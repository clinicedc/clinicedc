from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_constants.constants import FEMALE, MALE
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_screening.utils import get_subject_screening_model
from edc_sites import site_sites
from edc_utils import ceil_secs, floor_secs, formatted_date, formatted_datetime
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


@dataclass(order=True)
class ConsentDefinition:
    """A class that represents the general attributes
    of a consent.
    """

    proxy_model: str = field(compare=False)
    _ = KW_ONLY
    start: datetime = field(
        default=ResearchProtocolConfig().study_open_datetime,
        compare=True,
    )
    end: datetime = field(
        default=ResearchProtocolConfig().study_close_datetime,
        compare=False,
    )
    version: str = field(default="1", compare=False)
    updates: ConsentDefinition = field(default=None, compare=False)
    extends: ConsentDefinition = field(default=None, compare=False)
    screening_model: list[str] = field(default_factory=list, compare=False)
    age_min: int = field(default=18, compare=False)
    age_max: int = field(default=110, compare=False)
    age_is_adult: int = field(default=18, compare=False)
    gender: list[str] | None = field(default_factory=list, compare=False)
    site_ids: list[int] = field(default_factory=list, compare=False)
    country: str | None = field(default=None, compare=False)
    validate_duration_overlap_by_model: bool | None = field(default=True, compare=False)
    subject_type: str = field(default="subject", compare=False)
    timepoints: list[int] | None = field(default_factory=list, compare=False)

    name: str = field(init=False, compare=False)
    # set updated_by when the cdef is registered, see site_consents
    updated_by: ConsentDefinition = field(default=None, compare=False, init=False)
    extended_by: ConsentDefinitionExtension = field(
        default=None,
        compare=False,
        init=False,
    )
    _model: str = field(init=False, compare=False)
    sort_index: str = field(init=False)

    def __post_init__(self):
        self.model = self.proxy_model
        self.name = f"{self.proxy_model}-{self.version}"
        self.sort_index = self.name
        self.gender = [MALE, FEMALE] if not self.gender else self.gender
        if not self.screening_model:
            self.screening_model = [get_subject_screening_model()]
        if MALE not in self.gender and FEMALE not in self.gender:
            raise ConsentDefinitionError(f"Invalid gender. Got {self.gender}.")
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if str(self.start.tzinfo).upper() != "UTC":
            raise ConsentDefinitionError(
                f"Start date must be UTC. Got {self.start} / {self.start.tzinfo}."
            )
        if not self.end.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed Got {self.end}.")
        if str(self.end.tzinfo).upper() != "UTC":
            raise ConsentDefinitionError(
                f"End date must be UTC. Got {self.end} / {self.start.tzinfo}."
            )
        self.check_date_within_study_period()

    def model_create(self, **kwargs) -> ConsentLikeModel:
        """Creates a consent model instance and inserts version."""
        kwargs.update(version=self.version)
        return self.model_cls.objects.create(**kwargs)

    @property
    def model(self):
        from .managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager

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
        subject_identifier: str = None,
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
            f"from {formatted_date(to_local(self.start))} to "
            f"{formatted_date(to_local(self.end))}"
        )

    @property
    def verbose_name(self) -> str:
        return self.model_cls._meta.verbose_name

    def valid_for_datetime_or_raise(self, report_datetime: datetime) -> None:
        if report_datetime and not (
            floor_secs(self.start) <= report_datetime <= ceil_secs(self.end)
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
        for attr in ["start", "end"]:
            if not (
                floor_secs(study_open_datetime)
                <= getattr(self, attr)
                <= ceil_secs(study_close_datetime)
            ):
                open_date_string = formatted_datetime(study_open_datetime)
                close_date_string = formatted_datetime(study_close_datetime)
                attr_date_string = formatted_datetime(getattr(self, attr))
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
