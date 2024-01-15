from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type
from uuid import UUID

from edc_appointment.constants import IN_PROGRESS_APPT, NEW_APPT
from edc_appointment.models import Appointment
from edc_utils import get_utcnow

from .dashboard_model_button import DashboardModelButton
from .model_button import ADD

__all__ = ["AppointmentButton"]


@dataclass
class AppointmentButton(DashboardModelButton):
    model_obj: Appointment = None
    labels: tuple[str, str, str] = field(default=("Appt", "Appt", "Appt"))
    btn_colors: tuple[str, str, str] = field(
        default=("btn-warning", "btn-default", "btn-default")
    )
    model_cls: Type[Appointment] = field(default=Appointment, init=False)

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
    def btn_color(self) -> str:
        btn_color = super().btn_color
        if (
            self.model_obj
            and self.model_obj.appt_datetime <= get_utcnow()
            and not self.model_obj.related_visit
        ):
            btn_color = self.btn_colors[ADD]
        return btn_color

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
