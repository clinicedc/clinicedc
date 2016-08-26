from django.test import TestCase
from django.utils import timezone

from edc_constants.constants import YES
from edc_example.models import Appointment, SubjectConsent, Enrollment

from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class TestAppointment(TestCase):

    def test_appointments_creation(self):
        """Text if appointment triggering method creates appointments."""
        subject_consent = SubjectConsent.objects.create(
            consent_datetime=timezone.now(),
            identity='111211111',
            confirm_identity='111211111',
            is_literate=YES)
        enrollment = Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        self.assertEqual(Appointment.objects.all().count(), 4)
