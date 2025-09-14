from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_constants.constants import YES
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
        agrees_to_extension: str = field(default=YES, compare=False)
        _meta: ...


@dataclass(order=True)
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

    model: str = field(compare=False)
    _ = KW_ONLY
    start: datetime = field(default=ResearchProtocolConfig().study_open_datetime, compare=True)
    version: str = field(default="1", compare=False)
    extends: ConsentDefinition = field(default=None, compare=False)
    timepoints: list[int] | None = field(default_factory=list, compare=False)
    site_ids: list[int] = field(default_factory=list, compare=False)
    country: str | None = field(default=None, compare=False)

    name: str = field(init=False, compare=False)
    sort_index: str = field(init=False)

    def __post_init__(self):
        self.name = f"{self.model}-{self.version}"
        self.sort_index = self.name
        if not self.start.tzinfo:
            raise ConsentDefinitionError(f"Naive datetime not allowed. Got {self.start}.")
        if str(self.start.tzinfo) != "UTC":
            raise ConsentDefinitionError(f"Start date must be UTC. Got {self.start}.")
        self.extends.check_date_within_study_period()

    def update_visit_collection(
        self,
        visits: VisitCollection = None,
        subject_identifier: str = None,
        site_id: str = None,
        original_visit_collection: VisitCollection = None,
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
