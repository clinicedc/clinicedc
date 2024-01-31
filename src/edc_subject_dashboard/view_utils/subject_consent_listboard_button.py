from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

__all__ = ["SubjectConsentListboardButton"]

from typing import TYPE_CHECKING, Type, TypeVar

from edc_pdutils.site import Site
from edc_protocol.research_protocol_config import ResearchProtocolConfig

from . import ModelButton

if TYPE_CHECKING:
    from edc_consent.model_mixins import ConsentModelMixin
    from edc_screening.model_mixins import ScreeningModelMixin

    ScreeningModel = TypeVar("ScreeningModel", bound=ScreeningModelMixin)
    ConsentModel = TypeVar("ConsentModel", bound=ConsentModelMixin)


@dataclass
class SubjectConsentListboardButton(ModelButton):
    """For the consent button on subject screening listboard"""

    screening_obj: ScreeningModel = None
    model_obj: ConsentModel = None
    model_cls: Type[ConsentModel] = None

    def __post_init__(self):
        self.model_cls = self.screening_obj.consent_definition.model_cls
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
        return "Consent"

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
