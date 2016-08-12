from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_constants.constants import IN_PROGRESS, NEW_APPT

from example.appointment_factory import AppointmentFactory
from example.models import TestModel, Appointment, SubjectVisit
from example.visit_schedule import example_visit_schedule


class TestRequiresAppointmentMixin(TestCase):

    def setUp(self):
        site_visit_schedules.registry = {}
        site_visit_schedules.register(example_visit_schedule)
        TestModel.objects.create()

    def test_get_appt_status_new(self):
        """Test if the appointment status is returned as new."""
        appt1 = Appointment.objects.get(visit_code=1000)
        self.assertEqual(appt1.get_appt_status(), NEW_APPT)

    def test_get_appt_status_in_progress(self):
        """Test if the appointment with status in progress will be returned."""
        appt1 = Appointment.objects.get(visit_code=1000)
        appt1.appt_datetime = timezone.now() + timedelta(days=2)
        appt1.best_appt_datetime = appt1.appt_datetime
        appt1.save(update_fields=['best_appt_datetime', 'appt_datetime'])
        SubjectVisit.objects.create(appointment=appt1, report_datetime=timezone.now())
        appt1.appt_status = IN_PROGRESS
        appt1.save(update_fields=['appt_status'])
        appt1 = Appointment.objects.get(visit_code=1000)
        self.assertEqual(appt1.get_appt_status(), IN_PROGRESS)

    def test_validate_visit_code_sequence(self):
        """Test if a valide visit code sequesnce is done."""
        Appointment.objects.all().delete()
        TestModel.objects.create()
        self.assertEqual(Appointment.objects.filter(visit_code__in=[1000, 2000]).count(), 2)

    def test_wrong_visit_code_sequence2(self):
        """Test if a valide visit code sequesnce is done."""
        Appointment.objects.all().delete()
        with self.assertRaises(ValidationError) as cm:
            AppointmentFactory(visit_code_sequence=1)
        self.assertEqual(
            '[\"Attempt to create or update appointment instance out of sequence. Got \'1000.1\'.\"]',
            str(cm.exception)
        )

#     def test_update_others_as_not_in_progress(self):
#         """Test if an appointment status changed to in_progress while there is another in_progress appointment,
#
#         others a updated to a different appointment status."""
#         Appointment.objects.all().delete()
#         self.assertEqual(Appointment.objects.all().count(), 0)
#         TestModel.objects.create()
#         appt1 = Appointment.objects.get(visit_code=1000)
#         print(appt1.visit_definition.__dict__)
#         appt2 = Appointment.objects.get(visit_code=2000)
#         print(appt2.visit_definition.__dict__)
#         appt1.appt_datetime = timezone.now() + timedelta(days=2)
#         appt1.best_appt_datetime = appt1.appt_datetime
#         appt1.save(update_fields=['best_appt_datetime', 'appt_datetime'])
#         SubjectVisit.objects.create(appointment=appt1, report_datetime=timezone.now())
#         appt1.appt_status = IN_PROGRESS
#         appt1.save(update_fields=['appt_status'])
#         appt1 = Appointment.objects.get(visit_code=1000)
#         self.assertEqual(appt1.get_appt_status(), IN_PROGRESS)
#         self.assertEqual(appt2.get_appt_status(), NEW_APPT)
#         appt2.appt_datetime = timezone.now() + timedelta(days=35)
#         appt2.best_appt_datetime = appt2.appt_datetime
#         appt2.save(update_fields=['best_appt_datetime', 'appt_datetime'])
#         appt2 = Appointment.objects.get(visit_code=2000)
#         SubjectVisit.objects.create(appointment=appt2, report_datetime=timezone.now())
#         appt2.appt_status = IN_PROGRESS
#         appt2.save(update_fields=['appt_status'])
#         appt2 = Appointment.objects.get(visit_code=2000)
#         self.assertEqual(appt2.get_appt_status(), IN_PROGRESS)
