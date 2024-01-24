from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from django.db import models

__all__ = ["SubjectConsentButton"]

from typing import TYPE_CHECKING, TypeVar

from django.contrib.sites.models import Site

from .dashboard_model_button import DashboardModelButton

if TYPE_CHECKING:
    from edc_consent.model_mixins import ConsentModelMixin

    ConsentModel = TypeVar("ConsentModel", bound=ConsentModelMixin)


@dataclass
class SubjectConsentButton(DashboardModelButton):
    model_obj: ConsentModel = None
    metadata_model_obj: models.Model = field(init=False)

    def __post_init__(self):
        self.model_cls = self.model_obj.__class__

    @property
    def color(self) -> str:
        return "success"

    @property
    def label(self) -> str:
        return ""

    @property
    def site(self) -> Site:
        return self.model_obj.site

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        kwargs = dict(subject_identifier=self.model_obj.subject_identifier)
        if self.appointment:
            kwargs.update(appointment=self.appointment.id)
        return kwargs
