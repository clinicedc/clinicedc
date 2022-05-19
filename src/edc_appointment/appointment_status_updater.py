from typing import Any

from edc_metadata.metadata_helper_mixin import MetaDataHelperMixin

from .constants import COMPLETE_APPT, IN_PROGRESS_APPT, INCOMPLETE_APPT


class AppointmentStatusUpdaterError(Exception):
    pass


class AppointmentStatusUpdater(MetaDataHelperMixin):

    instance_attr = "appointment"

    def __init__(self, appointment: Any):
        self.appointment = appointment
        if not getattr(self.appointment, "id", None):
            raise AppointmentStatusUpdaterError(
                "Appointment instance must exist. Got `id` is None"
            )
        if self.appointment.appt_status != IN_PROGRESS_APPT:
            self.update_others_from_in_progress()
            self.appointment.appt_status = IN_PROGRESS_APPT
            self.appointment.save_base(update_fields=["appt_status"])

    def update_others_from_in_progress(self):
        opts = dict(
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            appt_status=IN_PROGRESS_APPT,
        )
        for appointment in self.appointment.__class__.objects.filter(**opts).exclude(
            id=self.appointment.id
        ):
            if self.crf_metadata_required_exists or self.requisition_metadata_required_exists:
                appointment.appt_status = INCOMPLETE_APPT
            else:
                appointment.appt_status = COMPLETE_APPT
            appointment.save_base(update_fields=["appt_status"])
