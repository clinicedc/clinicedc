from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_model_wrapper import ModelWrapper
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import SCHEDULED
from ..model_wrappers import SubjectVisitModelWrapper
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = 'edc_visit_tracking.subjectvisit'


class TestModelWrapper(TestCase):

    helper_cls = Helper

    def setUp(self):
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

    def test_(self):
        model_obj = SubjectVisit()
        wrapper = MySubjectVisitModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, 'edc_visit_tracking.subjectvisit')
        self.assertEqual(wrapper.model_cls, SubjectVisit)

    def test_knows_appointment(self):
        self.helper.consent_and_enroll()
        appointment = Appointment.objects.all().order_by(
            'timepoint_datetime')[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED)
        wrapper = MySubjectVisitModelWrapper(model_obj=subject_visit)
        self.assertEqual(str(appointment.id), wrapper.appointment)
