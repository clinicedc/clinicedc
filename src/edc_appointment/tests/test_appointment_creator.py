import os

from django.conf import settings
from django.test import TestCase, tag
from edc_appointment import AppointmentCreator
from edc_visit_schedule import VisitSchedule, Schedule, Visit
from dateutil.relativedelta import relativedelta, SA, SU
from edc_appointment.models import Appointment
from datetime import datetime
from arrow.arrow import Arrow
from django.test.utils import override_settings


class TestAppointmentCreator(TestCase):

    def setUp(self):
        Appointment.objects.all().delete()
        self.subject_identifier = '12345'
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_appointment',
            visit_model='edc_appointment.subjectvisit',
            offstudy_model='edc_appointment.subjectoffstudy',
            death_report_model='edc_appointment.deathreport',
            enrollment_model='edc_appointment.enrollment',
            disenrollment_model='edc_appointment.disenrollment')

        self.schedule = Schedule(
            name='schedule',
            enrollment_model='edc_appointment.enrollment',
            disenrollment_model='edc_appointment.disenrollment')

        self.visit1000 = Visit(code='1000',
                               timepoint=0,
                               rbase=relativedelta(days=0),
                               rlower=relativedelta(days=0),
                               rupper=relativedelta(days=6))

        self.visit1000R = Visit(code='1000',
                                timepoint=0,
                                rbase=relativedelta(days=0),
                                rlower=relativedelta(days=1),
                                rupper=relativedelta(days=6))

        class Meta:
            label_lower = ''

        class Obj:
            subject_identifier = self.subject_identifier
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            facility_name = 'clinic'
            _meta = Meta()
        self.model_obj = Obj()

    def test_init(self):
        self.assertTrue(
            AppointmentCreator(model_obj=self.model_obj, visit=self.visit1000))

    def test_str(self):
        creator = AppointmentCreator(
            model_obj=self.model_obj, visit=self.visit1000)
        self.assertEqual(str(creator), self.subject_identifier)

    def test_repr(self):
        creator = AppointmentCreator(
            model_obj=self.model_obj, visit=self.visit1000)
        self.assertTrue(creator)

    def test_create(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, Arrow.fromdatetime(datetime(2017, 1, 3)).datetime)

    @tag('4')
    @override_settings(
        HOLIDAY_FILE=os.path.join(settings.BASE_DIR, settings.APP_NAME, 'tests', 'no_holidays.csv'))
    def test_create_no_holidays(self):
        for i in range(1, 7):
            appt_datetime = Arrow.fromdatetime(datetime(2017, 1, i)).datetime
            if appt_datetime.weekday() not in [SA.weekday, SU.weekday]:
                break
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)
        self.assertEqual(
            Appointment.objects.all()[0], creator.appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, appt_datetime)

    def test_create_forward(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, Arrow.fromdatetime(datetime(2017, 1, 3)).datetime)

    @tag('1')
    def test_create_reverse(self):
        appt_datetime = Arrow.fromdatetime(datetime(2017, 1, 4)).datetime
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000R,
            suggested_datetime=appt_datetime)
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, Arrow.fromdatetime(datetime(2017, 1, 3)).datetime)

    def test_raise_on_naive_datetime(self):
        appt_datetime = datetime(2017, 1, 1)
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)

    def test_raise_on_naive_datetime2(self):
        appt_datetime = datetime(2017, 1, 1)
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime,
            timepoint_datetime=appt_datetime)
