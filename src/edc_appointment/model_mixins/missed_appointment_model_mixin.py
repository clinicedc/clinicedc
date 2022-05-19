from typing import Any

from django.db import models
from edc_visit_tracking.reason_updater import SubjectVisitReasonUpdater

from ..constants import IN_PROGRESS_APPT, MISSED_APPT


class MissedAppointmentModelMixin(models.Model):
    def create_missed_visit_from_appointment(self: Any):
        if self.appt_timing == MISSED_APPT:
            self.visit_model_cls().objects.create_missed_from_appointment(
                appointment=self,
            )

    def update_subject_visit_reason_or_raise(self: Any):
        """Trys to update the subject_visit.reason field, if it
        exists, when appt_timing changes, or raises.
        """
        if (
            self.id
            and self.appt_status == IN_PROGRESS_APPT
            and self.appt_timing
            and self.appt_reason
        ):
            reason_updater = SubjectVisitReasonUpdater(
                appointment=self,
                appt_timing=self.appt_timing,
                appt_reason=self.appt_reason,
            )
            reason_updater.update_or_raise()

    class Meta:
        abstract = True
