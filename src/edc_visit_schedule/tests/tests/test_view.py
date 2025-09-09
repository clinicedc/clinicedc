from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings, tag
from django.views.generic.base import ContextMixin

from edc_consent.site_consents import site_consents
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.models import OnSchedule
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin
from edc_visit_schedule.visit_schedule import VisitSchedule
from tests.consents import consent_v1
from tests.helper import Helper
from tests.sites import all_sites


class MyView(VisitScheduleViewMixin, ContextMixin):

    def __init__(self, **kwargs):
        self.subject_identifier = None
        super().__init__(**kwargs)

    def get_context_data(self, subject_identifier=None, **kwargs):
        self.subject_identifier = subject_identifier
        return super().get_context_data(subject_identifier=None, **kwargs)


class MyViewCurrent(VisitScheduleViewMixin, ContextMixin):

    def __init__(self, **kwargs):
        self.subject_identifier = None
        super().__init__(**kwargs)

    def get_context_data(self, subject_identifier=None, **kwargs):
        self.subject_identifier = subject_identifier
        return super().get_context_data(subject_identifier=None, **kwargs)


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=10)
class TestViewMixin(SiteTestCaseMixin, TestCase):
    def setUp(self):
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_offstudy.SubjectOffstudy",
            death_report_model="tests.DeathReport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.OnSchedule",
            offschedule_model="edc_visit_schedule.OffSchedule",
            consent_definitions=[consent_v1],
            appointment_model="edc_appointment.appointment",
        )
        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="tests.OnScheduleThree",
            offschedule_model="tests.OffScheduleThree",
            consent_definitions=[consent_v1],
            appointment_model="edc_appointment.appointment",
        )

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        helper = Helper()
        consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            consent_definition=consent_v1,
        )
        self.subject_identifier = consent.subject_identifier

    def test_context(self):
        view = MyView()
        view.request = RequestFactory()
        view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}
        context = view.get_context_data()
        self.assertIn("visit_schedules", context)
        self.assertIn("onschedule_models", context)

    def test_context_not_on_schedule(self):
        view = MyView()
        view.request = RequestFactory()
        view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}
        context = view.get_context_data(subject_identifier="12345")
        self.assertEqual(context.get("visit_schedules"), {})
        self.assertEqual(context.get("onschedule_models"), [])

    def test_context_on_schedule(self):
        view = MyView()
        view.request = RequestFactory()
        view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}
        context = view.get_context_data(subject_identifier=self.subject_identifier)
        self.assertEqual(
            context.get("visit_schedules"),
            {self.visit_schedule.name: self.visit_schedule},
        )
        obj = OnSchedule.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(context.get("onschedule_models"), [obj])

    def test_context_enrolled_current(self):
        view_current = MyViewCurrent()
        view_current.request = RequestFactory()
        view_current.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}
        context = view_current.get_context_data(
            subject_identifier=self.subject_identifier
        )
        obj = OnSchedule.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(context.get("current_onschedule_model"), obj)
        context.get("current_onschedule_model")
