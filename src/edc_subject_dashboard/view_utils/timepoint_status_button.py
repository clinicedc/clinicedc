from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from edc_appointment.constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
    SKIPPED_APPT,
)
from edc_utils import get_utcnow

from .appointment_button import AppointmentButton

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin

    RelatedVisitModel = TypeVar("RelatedVisitModel", bound=VisitModelMixin)

__all__ = ["TimepointStatusButton"]

NEW = 2
NEW_LATE = 0
COMPLETE = 1
INCOMPLETE = 3
CANCELLED = 2
SKIPPED = 2


@dataclass
class TimepointStatusButton(AppointmentButton):
    labels: tuple[str, str, str] = field(default=("Start", "Visit Report", "Visit Report"))
    btn_colors: tuple[str, str, str, str] = field(
        default=("btn-warning", "btn-success", "btn-default", "btn-danger")
    )

    @property
    def title(self) -> str:
        title = super().title
        if self.model_obj.appt_status == SKIPPED_APPT:
            title = "Skipped as per protocol"
        elif self.model_obj.appt_status == CANCELLED_APPT:
            title = "Cancelled"
        elif self.model_obj.appt_status == COMPLETE_APPT:
            title = "Done. All required forms submitted. Click to re-open"
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            title = "Incomplete. Some forms not submitted. Click to re-open"
        elif self.model_obj.appt_status == NEW_APPT:
            title = "Start appointment"
        if self.perms.view_only:
            title = f"{title} (view only)"
        return title

    @property
    def label(self) -> str:
        label = None
        if self.model_obj.appt_status == SKIPPED_APPT:
            label = "Skipped"
        elif self.model_obj.appt_status == CANCELLED_APPT:
            label = "Cancelled"
        elif self.model_obj.appt_status == COMPLETE_APPT:
            label = "Done"
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            label = "Incomplete"
        elif self.model_obj.appt_status == NEW_APPT:
            label = "Start"
        return label

    @property
    def btn_color(self) -> str:
        btn_color = super().btn_color
        if self.model_obj.appt_status in [COMPLETE_APPT, SKIPPED_APPT]:
            btn_color = self.btn_colors[COMPLETE]  # success / gree
        elif self.model_obj.appt_status == CANCELLED_APPT:
            btn_color = self.btn_colors[CANCELLED]  # default / grey
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            btn_color = self.btn_colors[INCOMPLETE]  # default / grey
        elif self.model_obj.appt_status == NEW_APPT:
            if self.model_obj.appt_datetime <= get_utcnow():
                btn_color = self.btn_colors[NEW_LATE]  # warning / orange
            else:
                btn_color = self.btn_colors[NEW]
        return btn_color

    @property
    def disabled(self) -> str:
        disabled = "disabled"
        if not self.model_obj and self.perms.add:
            disabled = ""
        else:
            if self.perms.change or self.perms.view:
                disabled = ""
        return disabled
