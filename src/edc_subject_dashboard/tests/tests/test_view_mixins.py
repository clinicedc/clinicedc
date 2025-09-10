from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings
from django.views.generic.base import ContextMixin
from edc_test_utils.get_httprequest_for_tests import get_request_object_for_tests
from edc_test_utils.get_user_for_tests import get_user_for_tests

from edc_appointment.models import Appointment
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_consent import site_consents
from edc_locator.exceptions import SubjectLocatorViewMixinError
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_sites.view_mixins import SiteViewMixin
from edc_subject_dashboard.view_mixins import (
    RegisteredSubjectViewMixin,
    SubjectVisitViewMixin,
    SubjectVisitViewMixinError,
)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import TestModel
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestViewMixins(TestCase):
    def setUp(self):

        self.user = get_user_for_tests()

        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = consent.subject_identifier

        self.appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            reason=SCHEDULED,
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
