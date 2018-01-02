import arrow

from datetime import datetime
from django.test import TestCase, tag
from edc_base import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import NEW_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT
from ..models import Appointment
from ..creators import InvalidParentAppointmentMissingVisitError
from ..creators import InvalidParentAppointmentStatusError
from ..creators import UnscheduledAppointmentCreator
from ..creators import UnscheduledAppointmentNotAllowed
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2


class TestUnscheduledAppointmentCreator(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = '12345'
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=arrow.Arrow.fromdatetime(
                datetime(2017, 1, 7), tzinfo='UTC').datetime)

    def test_unscheduled_allowed_but_raises_on_appt_status(self):
        self.helper.consent_and_put_on_schedule()
        schedule_name = 'schedule1'
        visit = visit_schedule1.schedules.get(schedule_name).visits.first
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=visit.code)
        # subject_visit not created so expect exception because of
        # the missing subject_visit
        for appt_status in [NEW_APPT, IN_PROGRESS_APPT, CANCELLED_APPT]:
            with self.subTest(appt_status=appt_status):
                appointment.appt_status = appt_status
                appointment.save()
                self.assertEqual(appointment.appt_status, appt_status)
                self.assertRaises(
                    InvalidParentAppointmentMissingVisitError,
                    UnscheduledAppointmentCreator,
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code)
        # add a subject_visit and expect exception to be raises because
        # of appt_status
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=get_utcnow())
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=visit.code)
        self.assertEqual(appointment.visit, subject_visit)
        for appt_status in [NEW_APPT, IN_PROGRESS_APPT, CANCELLED_APPT]:
            with self.subTest(appt_status=appt_status):
                appointment.appt_status = appt_status
                appointment.save()
                self.assertEqual(appointment.appt_status, appt_status)
                self.assertRaises(
                    InvalidParentAppointmentStatusError,
                    UnscheduledAppointmentCreator,
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code)

    def test_unscheduled_not_allowed(self):
        self.assertRaises(
            UnscheduledAppointmentNotAllowed,
            UnscheduledAppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=visit_schedule2.name,
            schedule_name='schedule2',
            visit_code='5000')

    def test_add_subject_visits(self):
        self.helper.consent_and_put_on_schedule()
        schedule_name = 'schedule1'
        for visit in visit_schedule1.schedules.get(schedule_name).visits.values():
            with self.subTest(visit=visit):
                # get parent appointment
                appointment = Appointment.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_code=visit.code)
                appointment.appt_status = IN_PROGRESS_APPT
                appointment.save()
                subject_visit = SubjectVisit.objects.create(
                    appointment=appointment,
                    report_datetime=get_utcnow())
                appointment = Appointment.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_code=visit.code,
                    visit_code_sequence=0)
                self.assertTrue(appointment.visit, subject_visit)
                self.assertEqual(0, appointment.visit.visit_code_sequence)
                self.assertEqual(1, appointment.next_visit_code_sequence)

                appointment.appt_status = INCOMPLETE_APPT
                appointment.save()

                creator = UnscheduledAppointmentCreator(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code,
                    facility=appointment.facility)
                new_appointment = creator.appointment
                self.assertEqual(new_appointment.appt_status, IN_PROGRESS_APPT)

                subject_visit = SubjectVisit.objects.create(
                    appointment=new_appointment,
                    report_datetime=get_utcnow())
                self.assertEqual(1, new_appointment.visit_code_sequence)
                self.assertEqual(1, subject_visit.visit_code_sequence)
                new_appointment.appt_status = INCOMPLETE_APPT
                new_appointment.save()
                self.assertEqual(new_appointment.appt_status, INCOMPLETE_APPT)
