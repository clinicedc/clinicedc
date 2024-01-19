from django.test import TestCase, override_settings
from django.views.generic.base import ContextMixin
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_locator.exceptions import SubjectLocatorViewMixinError
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_sites.utils import get_site_model_cls
from edc_sites.view_mixins import SiteViewMixin
from edc_test_utils.get_httprequest_for_tests import get_request_object_for_tests
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_subject_dashboard.view_mixins import (
    RegisteredSubjectViewMixin,
    SubjectVisitViewMixin,
    SubjectVisitViewMixinError,
)
from subject_dashboard_app.models import (
    Appointment,
    BadSubjectVisit,
    SubjectConsent,
    TestModel,
)

from .test_case_mixin import TestCaseMixin


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


@override_settings(SITE_ID=110)
class TestViewMixins(TestCaseMixin, TestCase):
    def setUp(self):
        self.subject_identifier = "101-108987-0"
        self.current_site = get_site_model_cls().objects.get_current()
        self.subject_identifier = "101-1234567-0"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "subject_dashboard_app.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
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

    def test_subject_visit_incorrect_relation(self):
        """Asserts raises if relation is not one to one."""

        class MySubjectVisitViewMixin(
            SubjectVisitViewMixin,
            RegisteredSubjectViewMixin,
            ContextMixin,
        ):
            visit_attr = "badsubjectvisit"

        mixin = MySubjectVisitViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertRaises(SubjectVisitViewMixinError, mixin.get_context_data)

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin,
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            AppointmentViewMixin,
            ContextMixin,
        ):
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertRaises(LookupError, mixin.get_context_data)

    def test_subject_locator_ok(self):
        class MySubjectLocatorViewMixin(
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            AppointmentViewMixin,
            ContextMixin,
        ):
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
