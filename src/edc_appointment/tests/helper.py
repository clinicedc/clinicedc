from edc_base.utils import get_utcnow

from .models import SubjectConsent, EnrollmentOne
from ..unscheduled_appointment_creator import UnscheduledAppointmentCreator


class Helper:

    def __init__(self, subject_identifier=None, now=None, facility_name=None):
        self.subject_identifier = subject_identifier
        self.now = now or get_utcnow()
        self.facility_name = facility_name

    def consent_and_enroll(self, subject_identifier=None, facility_name=None):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=self.now)
        EnrollmentOne.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            is_eligible=True,
            facility_name=facility_name or self.facility_name)

    def add_unscheduled_appointment(self, appointment=None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility)
        return creator.appointment
