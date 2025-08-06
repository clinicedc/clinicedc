from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_constants.constants import INCOMPLETE
from edc_visit_tracking.constants import MISSED_VISIT

from ..appointment_reason_updater import AppointmentReasonUpdater
from ..constants import IN_PROGRESS_APPT, MISSED_APPT

if TYPE_CHECKING:
    from ..models import Appointment


class MissedAppointmentModelMixin(models.Model):
    def create_missed_visit_from_appointment(self: Appointment):
        if self.appt_timing == MISSED_APPT:
            try:
                subject_visit = self.related_visit_model_cls().objects.get(
                    appointment__id=self.id
                )
            except ObjectDoesNotExist:
                self.related_visit_model_cls().objects.create_missed_from_appointment(
                    appointment=self,
                )
            else:
                subject_visit.reason = MISSED_VISIT
                subject_visit.document_status = INCOMPLETE
                subject_visit.save_base(update_fields=["reason", "document_status"])

    def update_subject_visit_reason_or_raise(self: Appointment):
        """Trys to update the subject_visit.reason field, if it
        exists, when appt_timing changes, or raises.
        """
        if (
            self.id
            and self.related_visit
            and self.appt_status == IN_PROGRESS_APPT
            and self.appt_timing
            and self.appt_reason
        ):
            AppointmentReasonUpdater(
                appointment=self,
                appt_timing=self.appt_timing,
                appt_reason=self.appt_reason,
                commit=True,
            )

    class Meta:
        abstract = True
