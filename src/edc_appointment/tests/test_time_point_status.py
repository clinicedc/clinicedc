from django.test import TestCase

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from example.models import TestModel, Appointment
from example.visit_schedule import example_visit_schedule

from edc_constants.constants import CLOSED, COMPLETE_APPT


class TestAppointmentMixin(TestCase):

    def setUp(self):
        site_visit_schedules.registry = {}
        site_visit_schedules.register(example_visit_schedule)
        TestModel.objects.create()
        self.appointments = Appointment.objects.all()

    def test_appointments_time_point_status_closed(self):
        """Text if appointment trigering method creates appointment."""
        appointment = self.appointments[0]
        appointment.appt_status = COMPLETE_APPT
        appointment.save()
        self.assertEqual(appointment.time_point_status, CLOSED)
