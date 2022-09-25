from datetime import date

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.views.generic.base import ContextMixin
from edc_consent import site_consents
from edc_consent.consent import Consent
from edc_constants.constants import FEMALE, MALE
from edc_protocol import Protocol
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin
from edc_visit_schedule.visit_schedule import VisitSchedule
from visit_schedule_app.models import OnSchedule, SubjectConsent


class MyView(VisitScheduleViewMixin, ContextMixin):
    kwargs: dict = {}


class MyViewCurrent(VisitScheduleViewMixin, ContextMixin):
    kwargs: dict = {}


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestViewMixin(SiteTestCaseMixin, TestCase):
    def setUp(self):
        v1_consent = Consent(
            "visit_schedule_app.subjectconsent",
            version="1",
            start=Protocol().study_open_datetime,
            end=Protocol().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="visit_schedule_app.SubjectOffstudy",
            death_report_model="visit_schedule_app.DeathReport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.OnSchedule",
            offschedule_model="visit_schedule_app.OffSchedule",
            consent_model="visit_schedule_app.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="visit_schedule_app.OnScheduleThree",
            offschedule_model="visit_schedule_app.OffScheduleThree",
            consent_model="visit_schedule_app.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        self.subject_identifier = "12345"
        self.view = MyView()
        self.view.kwargs = dict(subject_identifier=self.subject_identifier)
        self.view.subject_identifier = self.subject_identifier
        self.view.request = RequestFactory()
        self.view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

        self.view_current = MyViewCurrent()
        self.view_current.kwargs = dict(subject_identifier=self.subject_identifier)
        self.view_current.subject_identifier = self.subject_identifier
        self.view_current.request = RequestFactory()
        self.view_current.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345",
            consent_datetime=get_utcnow() - relativedelta(seconds=1),
            dob=date(1995, 1, 1),
            identity="11111",
            confirm_identity="11111",
        )

    def test_context(self):
        context = self.view.get_context_data()
        self.assertIn("visit_schedules", context)
        self.assertIn("onschedule_models", context)

    def test_context_not_on_schedule(self):
        context = self.view.get_context_data()
        self.assertEqual(context.get("visit_schedules"), {})
        self.assertEqual(context.get("onschedule_models"), [])

    def test_context_on_schedule(self):
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        context = self.view.get_context_data()
        self.assertEqual(
            context.get("visit_schedules"),
            {self.visit_schedule.name: self.visit_schedule},
        )
        self.assertEqual(context.get("onschedule_models"), [obj])

    def test_context_enrolled_current(self):
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        context = self.view_current.get_context_data()
        self.assertEqual(context.get("current_onschedule_model"), obj)
        context.get("current_onschedule_model")
