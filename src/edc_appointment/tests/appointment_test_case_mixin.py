from edc_visit_tracking.constants import UNSCHEDULED

from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment


class AppointmentTestCaseMixin:
    def get_appointment(
        self,
        subject_identifier=None,
        visit_code=None,
        visit_code_sequence=None,
        reason=None,
        appt_datetime=None,
    ):
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )
        if appt_datetime:
            appointment.appt_datetime = appt_datetime
            appointment.save()
            appointment.refresh_from_db()
        if reason == UNSCHEDULED:
            appointment = self.create_unscheduled_appointment(appointment)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()
        return appointment

    @staticmethod
    def create_unscheduled_appointment(appointment):
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        appt_creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
        )
        return appt_creator.appointment
