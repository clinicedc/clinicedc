from django.test import TestCase

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from example.models import TestModel, Appointment
from example.visit_schedule import example_visit_schedule


class TestAppointment(TestCase):

    def setUp(self):
        site_visit_schedules.registry = {}
        site_visit_schedules.register(example_visit_schedule)

    def test_appointments_creation(self):
        """Text if appointment trigering method creates appointment."""
        TestModel.objects.create()
        self.assertTrue(Appointment.objects.all().count() > 0)

    def test_appointments_creation_count(self):
        """Text if creates correct number of appointments."""
        TestModel.objects.create()
        visit_schedule = site_visit_schedules.get_visit_schedule(model=TestModel)
        schedule = visit_schedule.get_schedule(model=TestModel)
        self.assertEqual(Appointment.objects.all().count(), len(schedule.visits))

    def test_appointments_all_0(self):
        """Text if creates correct number of appointments."""
        TestModel.objects.create()
        visit_schedule = site_visit_schedules.get_visit_schedule(model=TestModel)
        schedule = visit_schedule.get_schedule(model=TestModel)
        self.assertEqual(Appointment.objects.filter(visit_code_sequence=0).count(), len(schedule.visits))

    def test_appointments_codes_match(self):
        """Text if creates appointments with matching codes."""
        TestModel.objects.create()
        visit_schedule = site_visit_schedules.get_visit_schedule(model=TestModel)
        schedule = visit_schedule.get_schedule(model=TestModel)
        for visit in schedule.visits.values():
            self.assertTrue(Appointment.objects.get(visit_code=visit.code))
