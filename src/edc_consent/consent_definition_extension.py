from __future__ import annotations

from datetime import datetime
from reprlib import recursive_repr
from typing import TYPE_CHECKING

from clinicedc_constants import YES
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites import site_sites
from edc_utils import formatted_date
from edc_utils.date import to_local
from edc_visit_schedule.schedule import VisitCollection

from .exceptions import ConsentDefinitionError

if TYPE_CHECKING:
    from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin

    from .consent_definition import ConsentDefinition

    class ConsentLikeModel(SiteModelMixin, UniqueSubjectIdentifierModelMixin, BaseUuidModel):
        _meta: ...

    class ConsentExtensionLikeModel(
        SiteModelMixin, UniqueSubjectIdentifierModelMixin, BaseUuidModel
    ):
        agrees_to_extension: str = YES
        _meta: ...


class ConsentDefinitionExtension:
    """A definition to truncate the number of visits/timepoints in a
    visit collection for a consented subject, if necessary.

    If the consent extension model is complete for this subject and
    the field `agrees_to_extension` == YES, the visit collection
    is NOT truncated.

    For example, a trial originally consents to a 36m followup. At some
    point the trial receives approval to extend followup to 48m for
    those who agree. For those who DO NOT agree to the extended
    followup, the timepoints defined in this extension are removed
    from the given visit collection.

    Note: See also `Schedule`. The schedule should be defined with
    all possible visits/timepoints. That is, if approval is for 48m
    of followup, the Schedule should be defined with 48m of followup.
    This class will remove, not add, visits/timepoints from the given
    visit collection if necessary.
    """

    def __init__(
        self,
        model: str,
        *,
        start: datetime | None = None,
        version: str | None = None,
        extends: ConsentDefinition | None = None,
        timepoints: list[int] | None = None,
        site_ids: list[int] | None = None,
        country: str | None = None,
    ) -> None:

        self.model = model
        self.start: datetime = start or ResearchProtocolConfig().study_open_datetime

        self.version = version or "1"
        self.extends = extends
        self.timepoints = timepoints or []
        self.site_ids = site_ids or []
        self.country = country

        self.name = f"{self.model}-{self.version}"
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        self.extends.check_date_within_study_period()

    def _cmp_values(self) -> tuple[datetime, str]:
        """Returns the values used by the comparison methods."""
        return self.start, self.name

    @recursive_repr()
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"model={self.model!r}, "
            f"start={self.start!r}, "
            f"version={self.version!r}, "
            f"extends={self.extends!r}, "
            f"timepoints={self.timepoints!r}, "
            f"site_ids={self.site_ids!r}, "
            f"country={self.country!r}, "
            f"name={self.name!r}, "
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

    def update_visit_collection(
        self,
        visits: VisitCollection,
        subject_identifier: str,
        site_id: int | None,
        *,
        original_visit_collection: VisitCollection,
    ) -> VisitCollection:
        """Returns the visit collection with or without the
        timepoints of this extension.

        `original_visit_collection` is unchanged.
        """
        if not self.get_consent_extension_for(
            subject_identifier=subject_identifier,
            site_id=site_id,
        ):
            for v in original_visit_collection.values():
                if v.timepoint in self.timepoints:
                    del visits[v.code]
        return visits

    @property
    def model_cls(self) -> type[ConsentExtensionLikeModel]:
        return django_apps.get_model(self.model)

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

    def get_consent_extension_for(self, **kwargs) -> ConsentExtensionLikeModel | None:
        """Returns the consent extension model instance for the
        parent consent definition.

        If field `agrees_to_extension` == YES, extension is granted.
        """
        subject_consent = self.get_consent_for(**kwargs)
        try:
            consent_extension_obj = self.model_cls.objects.get(
                subject_consent=subject_consent,
                report_datetime__gte=self.start,
                agrees_to_extension=YES,
            )
        except ObjectDoesNotExist:
            consent_extension_obj = None
        return consent_extension_obj

    def get_consent_for(self, **kwargs) -> ConsentLikeModel | None:
        """Returns the parent consent model instance for the subject."""
        return self.extends.get_consent_for(**kwargs)

    @property
    def display_name(self) -> str:
        return (
            f"{self.model_cls._meta.verbose_name} v{self.version} valid "
            f"from {formatted_date(to_local(self.start))} to "
            f"{formatted_date(to_local(self.extends.end))}"
        )

    @property
    def verbose_name(self) -> str:
        return self.model_cls._meta.verbose_name
