from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from django.utils import timezone

from edc_consent import site_consents
from edc_pdutils.site import Site
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_view_utils import ModelButton

if TYPE_CHECKING:
    from edc_consent.model_mixins import ConsentModelMixin
    from edc_screening.model_mixins import ScreeningModelMixin

    ScreeningModel = TypeVar("ScreeningModel", bound=ScreeningModelMixin)
    ConsentModel = TypeVar("ConsentModel", bound=ConsentModelMixin)

__all__ = ["SubjectConsentListboardButton"]


@dataclass
class SubjectConsentListboardButton(ModelButton):
    """For the consent button on subject screening listboard.

    Note: model_cls comes from the consent definition. The consent
    definition is selected by date. If there are multiple consent
    versions using different consent model classes, the date used to
    select the consent definition might matter. This may be a problem
    if data is not collected in realtime. That is, if there is a
    duration between the screening report_datetime and the date the
    consent button is rendered and clicked that crosses over from
    consent version 1 to version 2.
    """

    screening_obj: ScreeningModel = field(default=None)
    model_obj: ConsentModel = field(default=None)
    model_cls: type[ConsentModel] = field(default=None)
    consent_version: str = field(default=None, init=False)

    def __post_init__(self):
        cdef = site_consents.get_consent_definition(
            report_datetime=timezone.now(),
            screening_model=self.screening_obj._meta.label_lower,
        )
        self.model_cls = cdef.model_cls
        self.consent_version = cdef.version
        if self.screening_obj.consented:
            self.model_obj = self.model_cls.objects.get(
                subject_identifier=self.screening_obj.subject_identifier
            )
        if not self.next_url_name:
            self.next_url_name = "screening_listboard_url"

    @property
    def site(self) -> Site | None:
        return getattr(self.screening_obj, "site", None) or getattr(self.request, "site", None)

    @property
    def label(self) -> str:
        return f"Consent v{self.consent_version}"

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        kwargs = dict(screening_identifier=self.screening_obj.screening_identifier)
        if re.match(
            ResearchProtocolConfig().subject_identifier_pattern,
            self.screening_obj.subject_identifier,
        ):
            kwargs.update(subject_identifier=self.screening_obj.subject_identifier)
        return kwargs

    @property
    def extra_kwargs(self) -> dict[str, str | int]:
        return dict(
            gender=self.screening_obj.gender,
            initials=self.screening_obj.initials,
            site=self.screening_obj.site.id,
        )
