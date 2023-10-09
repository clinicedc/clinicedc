from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.views.generic.base import ContextMixin
from edc_facility import import_holidays
from edc_locator.view_mixins import (
    SubjectLocatorViewMixin,
    SubjectLocatorViewMixinError,
)
from edc_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_subject_dashboard.view_mixins import (
    SubjectVisitViewMixin,
    SubjectVisitViewMixinError,
)

from ..models import Appointment, BadSubjectVisit, OnScheduleOne, TestModel
from ..visit_schedule import visit_schedule1


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


class TestViewMixins(TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )

        self.subject_identifier = "12345"

        onschedule_datetime = get_utcnow() - relativedelta(years=1)

        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            registration_datetime=onschedule_datetime,
        )

        OnScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )

        self.appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            visit_code="1000",
            reason=SCHEDULED,
        )
        self.bad_subject_visit = BadSubjectVisit.objects.create(
            appointment=self.appointment, subject_identifier=self.subject_identifier
        )
        self.test_model = TestModel.objects.create(subject_visit=self.subject_visit)

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def test_subject_visit_missing_appointment(self):
        class MyView(SubjectVisitViewMixin, ContextMixin):
            pass

        view = MyView()
        self.assertRaises(SubjectVisitViewMixinError, view.get_context_data)

    def test_subject_visit_correct_relation(self):
        class MyView(SubjectVisitViewMixin, ContextMixin):
            pass

        view = MyView()
        view.appointment = self.appointment
        context = view.get_context_data()
        self.assertEqual(context.get("related_visit"), self.subject_visit)

    def test_subject_visit_incorrect_relation(self):
        """Asserts raises if relation is not one to one."""

        class MySubjectVisitViewMixin(SubjectVisitViewMixin, ContextMixin):
            visit_attr = "badsubjectvisit"

        mixin = MySubjectVisitViewMixin()
        self.assertRaises(SubjectVisitViewMixinError, mixin.get_context_data)

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin, ContextMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        self.assertRaises(SubjectLocatorViewMixinError, mixin.get_context_data)

    def test_subject_locator_raisesmissing_wrapper_cls(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin, ContextMixin):
            subject_locator_model = "edc_locator.subjectlocator"

        self.assertRaises(SubjectLocatorViewMixinError, MySubjectLocatorViewMixin)

    def test_subject_locator_ok(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin, ContextMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
