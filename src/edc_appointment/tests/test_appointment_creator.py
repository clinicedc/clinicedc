import os

from arrow.arrow import Arrow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_base.utils import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule import VisitSchedule, Schedule, Visit

from ..creators import AppointmentCreator
from ..models import Appointment


class TestAppointmentCreator(TestCase):

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        Appointment.objects.all().delete()
        self.subject_identifier = '12345'
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            offstudy_model='edc_appointment.subjectoffstudy',
            death_report_model='edc_appointment.deathreport')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_appointment.onschedule',
            offschedule_model='edc_appointment.offschedule',
            appointment_model='edc_appointment.appointment',
            consent_model='edc_appointment.subjectconsent')

        self.visit1000 = Visit(code='1000',
                               timepoint=0,
                               rbase=relativedelta(days=0),
                               rlower=relativedelta(days=0),
                               rupper=relativedelta(days=6),
                               facility_name='7-day-clinic')

        self.visit1000R = Visit(code='1000',
                                timepoint=0,
                                rbase=relativedelta(days=0),
                                rlower=relativedelta(days=1),
                                rupper=relativedelta(days=6),
                                facility_name='7-day-clinic')
        app_config = django_apps.get_app_config('edc_facility')

        class Meta:
            label_lower = ''

        class DummyAppointmentObj:
            subject_identifier = self.subject_identifier
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            facility = app_config.get_facility(name='7-day-clinic')
            _meta = Meta()

        self.model_obj = DummyAppointmentObj()

    def test_init(self):
        self.assertTrue(
            AppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule.name,
                schedule_name=self.schedule.name,
                visit=self.visit1000,
                timepoint_datetime=get_utcnow()))

    def test_str(self):
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow())
        self.assertEqual(str(creator), self.subject_identifier)

    def test_repr(self):
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow())
        self.assertTrue(creator)

    def test_create(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime,
            Arrow.fromdatetime(datetime(2017, 1, 3)).datetime)

    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, settings.APP_NAME, 'tests', 'no_holidays.csv'))
    def test_create_no_holidays(self):
        for i in range(1, 7):
            appt_datetime = Arrow.fromdatetime(datetime(2017, 1, i)).datetime
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime)
        self.assertEqual(
            Appointment.objects.all()[0], creator.appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, appt_datetime)

    def test_create_forward(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime,
            Arrow.fromdatetime(datetime(2017, 1, 3)).datetime)

    def test_create_reverse(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 10)).datetime
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000R,
            timepoint_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime,
            Arrow.fromdatetime(datetime(2017, 1, 9)).datetime)

    def test_raise_on_naive_datetime(self):
        appt_datetime = datetime(2017, 1, 1)
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime)

    def test_raise_on_naive_datetime2(self):
        appt_datetime = datetime(2017, 1, 1)
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime)
