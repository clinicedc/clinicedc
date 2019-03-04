from django.test import TestCase, tag
from edc_utils import get_utcnow
from edc_locator.view_mixins import (
    SubjectLocatorViewMixin,
    SubjectLocatorViewMixinError,
)
from edc_registration.models import RegisteredSubject
from edc_visit_schedule import site_visit_schedules

from ..view_mixins import SubjectVisitViewMixin, SubjectVisitViewMixinError
from .models import SubjectVisit, TestModel, BadSubjectVisit, Appointment
from .visit_schedule import visit_schedule1


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


class TestViewMixins(TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

        RegisteredSubject.objects.create(subject_identifier="12345")

        self.appointment = Appointment.objects.create(
            visit_code="1000",
            appt_datetime=get_utcnow(),
            visit_schedule_name="visit_schedule1",
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, subject_identifier="12345"
        )
        self.bad_subject_visit = BadSubjectVisit.objects.create(
            appointment=self.appointment, subject_identifier="12345"
        )
        self.test_model = TestModel.objects.create(subject_visit=self.subject_visit)

    def test_subject_visit_missing_appointment(self):
        mixin = SubjectVisitViewMixin()
        self.assertRaises(SubjectVisitViewMixinError, mixin.get_context_data)

    def test_subject_visit_correct_relation(self):
        mixin = SubjectVisitViewMixin()
        mixin.appointment = self.appointment
        context = mixin.get_context_data()
        self.assertEqual(context.get("subject_visit"), self.subject_visit)

    def test_subject_visit_incorrect_relation(self):
        """Asserts raises if relation is not one to one.
        """

        class MySubjectVisitViewMixin(SubjectVisitViewMixin):
            visit_attr = "badsubjectvisit"

        mixin = MySubjectVisitViewMixin()
        mixin.appointment = self.appointment
        self.assertRaises(SubjectVisitViewMixinError, mixin.get_context_data)

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        self.assertRaises(SubjectLocatorViewMixinError, mixin.get_context_data)

    def test_subject_locator_raisesmissing_wrapper_cls(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model = "edc_locator.subjectlocator"

        self.assertRaises(SubjectLocatorViewMixinError, MySubjectLocatorViewMixin)

    def test_subject_locator_ok(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": "12345"}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
