from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_visit_schedule import site_visit_schedules

from ..model_wrappers import SubjectVisitModelWrapper
from .models import SubjectVisit, Appointment
from .visit_schedule import visit_schedule1


class MySubjectVisitModelWrapper(SubjectVisitModelWrapper):

    model = "edc_subject_dashboard.subjectvisit"


class TestModelWrapper(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

    @tag("1")
    def test_(self):
        model_obj = SubjectVisit()
        wrapper = MySubjectVisitModelWrapper(model_obj=model_obj)
        self.assertEqual(wrapper.model, "edc_subject_dashboard.subjectvisit")
        self.assertEqual(wrapper.model_cls, SubjectVisit)

    @tag("1")
    def test_knows_appointment(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            appt_reason="scheduled",
            visit_schedule_name="visit_schedule1",
        )
        subject_visit = SubjectVisit.objects.create(appointment=appointment)
        wrapper = MySubjectVisitModelWrapper(model_obj=subject_visit)
        self.assertEqual(str(appointment.id), wrapper.appointment)
