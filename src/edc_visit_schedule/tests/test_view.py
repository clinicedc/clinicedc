from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.test.utils import override_settings
from edc_sites.tests import SiteTestCaseMixin

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..view_mixins import VisitScheduleViewMixin
from ..visit_schedule import VisitSchedule
from .models import OnSchedule


class TestView(VisitScheduleViewMixin):

    kwargs = {}


class TestViewCurrent(VisitScheduleViewMixin):

    kwargs = {}

    def is_current_onschedule_model(self, onschedule_instance, **kwargs):
        return True


@override_settings(SITE_ID=40)
class TestViewMixin(SiteTestCaseMixin, TestCase):
    def setUp(self):
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.SubjectOffstudy",
            death_report_model="edc_visit_schedule.DeathReport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.OnSchedule",
            offschedule_model="edc_visit_schedule.OffSchedule",
            consent_model="edc_appointment.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="edc_visit_schedule.OnScheduleThree",
            offschedule_model="edc_visit_schedule.OffScheduleThree",
            consent_model="edc_appointment.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        self.subject_identifier = "12345"
        self.view = TestView()
        self.view.kwargs = dict(subject_identifier=self.subject_identifier)
        self.view.subject_identifier = self.subject_identifier
        self.view.request = RequestFactory()
        self.view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

        self.view_current = TestViewCurrent()
        self.view_current.kwargs = dict(subject_identifier=self.subject_identifier)
        self.view_current.subject_identifier = self.subject_identifier
        self.view_current.request = RequestFactory()
        self.view_current.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

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
        obj = context.get("current_onschedule_model")
