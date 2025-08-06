from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type
from uuid import UUID

from django.apps import apps as django_apps
from django.utils.translation import gettext as _
from edc_utils import get_utcnow
from edc_view_utils.dashboard_model_button import DashboardModelButton
from edc_view_utils.model_button import ADD

from ..constants import IN_PROGRESS_APPT, NEW_APPT

if TYPE_CHECKING:
    from ..models import Appointment


__all__ = ["AppointmentButton"]


@dataclass
class AppointmentButton(DashboardModelButton):
    model_obj: Appointment = None
    colors: tuple[str, str, str] = field(default=(3 * ("default",)))
    model_cls: Type[Appointment] = field(default=None, init=False)
    appointment: Appointment = field(default=None, init=False)

    def __post_init__(self):
        self.model_cls = django_apps.get_model("edc_appointment.appointment")

    @property
    def disabled(self) -> str:
        disabled = "disabled"
        if self.model_obj.appt_status == IN_PROGRESS_APPT and self.perms.change:
            disabled = ""
        elif (
            self.model_obj.appt_status != NEW_APPT
            and not self.perms.add
            and not self.perms.change
            and self.perms.view
        ):
            disabled = ""
        return disabled

    @property
    def label(self) -> str:
        return _("Appt")

    @property
    def color(self) -> str:
        color = super().color
        if (
            self.model_obj
            and self.model_obj.appt_datetime <= get_utcnow()
            and not self.model_obj.related_visit
        ):
            color = self.colors[ADD]
        return color

    @property
    def fa_icon(self) -> str:
        fa_icon = super().fa_icon
        if self.model_obj.appt_status == NEW_APPT:
            fa_icon = self.fa_icons[ADD]
        return fa_icon

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        return dict(
            subject_identifier=self.model_obj.subject_identifier,
        )

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        return dict(reason=self.model_obj.appt_reason)
