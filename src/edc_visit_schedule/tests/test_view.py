from django.test import TestCase, tag
from django.views.generic.base import ContextMixin
from django.test.client import RequestFactory
from uuid import uuid4

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..view_mixins import VisitScheduleViewMixin
from ..visit_schedule import VisitSchedule
from .models import OnSchedule


class TestView(VisitScheduleViewMixin, ContextMixin):
    pass


class TestViewCurrent(VisitScheduleViewMixin, ContextMixin):
    def is_current_onschedule_model(self, onschedule_instance, **kwargs):
        return True


class TestViewMixin(TestCase):

    def setUp(self):
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport',
            onschedule_model='edc_visit_schedule.OnSchedule',
            offschedule_model='edc_visit_schedule.OffSchedule')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.OnSchedule',
            offschedule_model='edc_visit_schedule.OffSchedule',
            appointment_model='edc_appointment.appointment')
        self.schedule3 = Schedule(
            name='schedule_three',
            onschedule_model='edc_visit_schedule.OnScheduleThree',
            offschedule_model='edc_visit_schedule.OffScheduleThree',
            appointment_model='edc_appointment.appointment')

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        self.subject_identifier = '12345'
        self.view = TestView()
        self.view.subject_identifier = self.subject_identifier
        self.view.request = RequestFactory()
        self.view.request.META = {'HTTP_CLIENT_IP': '1.1.1.1'}

        self.subject_identifier = '12345'
        self.view_current = TestViewCurrent()
        self.view_current.subject_identifier = self.subject_identifier
        self.view_current.request = RequestFactory()
        self.view_current.request.META = {'HTTP_CLIENT_IP': '1.1.1.1'}

    def test_context(self):
        context = self.view.get_context_data()
        self.assertIn('visit_schedules', context)
        self.assertIn('onschedule_models', context)

    def test_context_not_on_schedule(self):
        context = self.view.get_context_data()
        self.assertEqual(context.get('visit_schedules'), [])
        self.assertEqual(context.get('onschedule_models'), [])

    def test_context_on_schedule(self):
        obj = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            consent_identifier=uuid4())
        context = self.view.get_context_data()
        self.assertEqual(context.get('visit_schedules'), [self.visit_schedule])
        self.assertEqual(context.get('onschedule_models'), [obj])

    def test_context_enrolled_current(self):
        obj = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            consent_identifier=uuid4())
        context = self.view_current.get_context_data()
        self.assertEqual(context.get('current_onschedule_model'), obj)
        obj = context.get('current_onschedule_model')
        self.assertTrue(obj.current)
