from django.test import TestCase

from .test_visit_schedule import VisitSchedule
from example.models import TestModel, AppointmentTestModel


class TestAppointment(TestCase):

    def setUp(self):
        pass
        VisitSchedule().build()

    def test_appointments_creation(self):
        """Text if appoint trigering method creates appointment."""
        TestModel.objects.create()
        print(AppointmentTestModel.objects.all().count(), "NUmber of appointments")
