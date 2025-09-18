from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from django.utils import timezone
from django.utils.translation import gettext as _

from edc_appointment.constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
    SKIPPED_APPT,
)
from edc_appointment.view_utils import AppointmentButton

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
    colors: tuple[str, str, str, str] = field(
        default=("warning", "success", "default", "danger")
    )

    @property
    def title(self) -> str:
        title = _(super().title)
        if self.model_obj.appt_status == SKIPPED_APPT:
            title = _("Skipped as per protocol")
        elif self.model_obj.appt_status == CANCELLED_APPT:
            title = _("Cancelled")
        elif self.model_obj.appt_status == COMPLETE_APPT:
            title = _("Done. All required forms submitted. Click to re-open")
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            title = _("Incomplete. Some forms not submitted. Click to re-open")
        elif self.model_obj.appt_status == NEW_APPT:
            title = _("Start appointment")
        if self.perms.view_only:
            title = _("%(title)s (view only)") % {"title": title}
        return title

    @property
    def label(self) -> str:
        label = None
        if self.model_obj.appt_status == SKIPPED_APPT:
            label = _("Skipped")
        elif self.model_obj.appt_status == CANCELLED_APPT:
            label = _("Cancelled")
        elif self.model_obj.appt_status == COMPLETE_APPT:
            label = _("Done")
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            label = _("Incomplete")
        elif self.model_obj.appt_status == NEW_APPT:
            label = _("Start")
        return label

    @property
    def color(self) -> str:
        color = super().color
        if self.model_obj.appt_status in [COMPLETE_APPT, SKIPPED_APPT]:
            color = self.colors[COMPLETE]  # success / gree
        elif self.model_obj.appt_status == CANCELLED_APPT:
            color = self.colors[CANCELLED]  # default / grey
        elif self.model_obj.appt_status == INCOMPLETE_APPT:
            color = self.colors[INCOMPLETE]  # default / grey
        elif self.model_obj.appt_status == NEW_APPT:
            if self.model_obj.appt_datetime <= timezone.now():
                color = self.colors[NEW_LATE]  # warning / orange
            else:
                color = self.colors[NEW]
        return color

    @property
    def disabled(self) -> str:
        disabled = "disabled"
        if (not self.model_obj and self.perms.add) or self.perms.change or self.perms.view:
            disabled = ""
        return disabled
