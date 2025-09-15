from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

__all__ = ["SubjectConsentDashboardButton"]

from typing import TYPE_CHECKING, TypeVar

from edc_view_utils import ModelButton

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_consent.model_mixins import ConsentModelMixin

    ConsentModel = TypeVar("ConsentModel", bound=ConsentModelMixin)


@dataclass
class SubjectConsentDashboardButton(ModelButton):
    """For the subject dashboard"""

    model_obj: ConsentModel = None
    model_cls: type[ConsentModel] = None
    appointment: Appointment = None

    def __post_init__(self):
        self.model_cls = self.model_obj.__class__
        if not self.next_url_name:
            self.next_url_name = "subject_dashboard_url"

    @property
    def color(self) -> str:
        return "success"

    @property
    def label(self) -> str:
        return ""

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        kwargs = dict(subject_identifier=self.model_obj.subject_identifier)
        if self.appointment:
            kwargs.update(appointment=self.appointment.id)
        return kwargs
