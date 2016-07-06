from django.test import TestCase

from example.models import TestModel
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class TestAppointment(TestCase):

    def setUp(self):
        site_visit_schedules.registry = {}
        site_visit_schedules.register(example_visit_schedule)

    def test_appointments_creation(self):
        """Text if appoint trigering method creates appointment."""
        TestModel.objects.create()
