from typing import Any, Optional

from .constants import COMPLETE_APPT, IN_PROGRESS_APPT, INCOMPLETE_APPT


class AppointmentStatusUpdaterError(Exception):
    pass


class AppointmentStatusUpdater:
    def __init__(
        self,
        appointment: Any,
        change_to_in_progress: Optional[bool] = None,
        clear_others_in_progress: Optional[bool] = None,
    ):
        self.appointment = appointment
        if not getattr(self.appointment, "id", None):
            raise AppointmentStatusUpdaterError(
                "Appointment instance must exist. Got `id` is None"
            )
        if change_to_in_progress and self.appointment.appt_status != IN_PROGRESS_APPT:
            self.appointment.appt_status = IN_PROGRESS_APPT
            self.appointment.save_base(update_fields=["appt_status"])
        if clear_others_in_progress:
            self.update_others_from_in_progress()

    def update_others_from_in_progress(self):
        opts = dict(
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            appt_status=IN_PROGRESS_APPT,
        )
        appointments = self.appointment.__class__.objects.filter(**opts).exclude(
            id=self.appointment.id
        )
        for appointment in appointments:
            if not appointment.visit:
                appointment.appt_status = INCOMPLETE_APPT
            else:
                if (
                    appointment.crf_metadata_required_exists
                    or appointment.requisition_metadata_required_exists
                ):
                    appointment.appt_status = INCOMPLETE_APPT
                else:
                    appointment.appt_status = COMPLETE_APPT
            appointment.save_base(update_fields=["appt_status"])
            appointment.refresh_from_db()
