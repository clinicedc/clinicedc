from django.test import TestCase, tag
from django.views.generic.base import ContextMixin
from django.test.client import RequestFactory

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..view_mixins import VisitScheduleViewMixin
from ..visit_schedule import VisitSchedule
from .models import Enrollment


class TestView(VisitScheduleViewMixin, ContextMixin):
    pass


class TestViewCurrent(VisitScheduleViewMixin, ContextMixin):
    def is_current_enrollment_model(self, enrollment_instance, **kwargs):
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
            enrollment_model='edc_visit_schedule.Enrollment',
            disenrollment_model='edc_visit_schedule.Disenrollment')

        self.schedule = Schedule(
            name='schedule',
            enrollment_model='edc_visit_schedule.Enrollment',
            disenrollment_model='edc_visit_schedule.Disenrollment',
            appointment_model='edc_appointment.appointment')
        self.schedule3 = Schedule(
            name='schedule_three',
            enrollment_model='edc_visit_schedule.EnrollmentThree',
            disenrollment_model='edc_visit_schedule.DisenrollmentThree',
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
        self.assertIn('enrollment_models', context)

    def test_context_not_enrolled(self):
        context = self.view.get_context_data()
        self.assertEqual(context.get('visit_schedules'), [])
        self.assertEqual(context.get('enrollment_models'), [])

    def test_context_enrolled(self):
        obj = Enrollment.objects.create(
            subject_identifier=self.subject_identifier)
        context = self.view.get_context_data()
        self.assertEqual(context.get('visit_schedules'), [self.visit_schedule])
        self.assertEqual(context.get('enrollment_models'), [obj])

    def test_context_enrolled_current(self):
        obj = Enrollment.objects.create(
            subject_identifier=self.subject_identifier)
        context = self.view_current.get_context_data()
        self.assertEqual(context.get('current_enrollment_model'), obj)
        obj = context.get('current_enrollment_model')
        self.assertTrue(obj.current)
