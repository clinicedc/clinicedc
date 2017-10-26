from django.test import TestCase, tag
from edc_appointment.appointment_creator import AppointmentCreator
from edc_visit_schedule import VisitSchedule, Schedule, Visit
from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow
from edc_appointment.models.appointment import Appointment


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

        class Meta:
            label_lower = ''

        class Obj:
            subject_identifier = self.subject_identifier
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            facility_name = 'clinic'
            _meta = Meta()
        self.model_obj = Obj()

    @tag('1')
    def test_init(self):
        self.assertTrue(AppointmentCreator(model_obj=self.model_obj))

    @tag('1')
    def test_str(self):
        creator = AppointmentCreator(model_obj=self.model_obj)
        self.assertEqual(str(creator), self.subject_identifier)

    @tag('1')
    def test_repr(self):
        creator = AppointmentCreator(model_obj=self.model_obj)
        self.assertTrue(creator)

    @tag('1')
    def test_create(self):
        appt_datetime = get_utcnow()
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)
        creator.update_or_create()
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, appt_datetime)

    @tag('1')
    def test_create(self):
        appt_datetime = get_utcnow()
        creator = AppointmentCreator(
            model_obj=self.model_obj,
            visit=self.visit1000,
            suggested_datetime=appt_datetime)
        creator.update_or_create()
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime, appt_datetime)
