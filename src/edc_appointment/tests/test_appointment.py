from django.test import TestCase

# from .base_test_case import BaseTestCase
from .test_visit_schedule import VisitSchedule
from example.models import TestModel, AppointmentTestModel


class TestAppointment(TestCase):

    def setUp(self):
        VisitSchedule().build()

    def test_appointments_creation(self):
        """Text if appoint trigering method creates appointment."""
        TestModel.objects.create()
        AppointmentTestModel.objects.all().count()
