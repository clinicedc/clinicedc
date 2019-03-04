from django.test import TestCase
from edc_utils import get_utcnow

from .models import SubjectVisit, TestModel, BadSubjectVisit, Appointment


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


class TestPrintManifest(TestCase):
    def setUp(self):
        self.appointment = Appointment.objects.create(
            visit_code="1000", appt_datetime=get_utcnow()
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, subject_identifier="12345"
        )
        self.bad_subject_visit = BadSubjectVisit.objects.create(
            appointment=self.appointment, subject_identifier="12345"
        )
        self.test_model = TestModel.objects.create(subject_visit=self.subject_visit)
