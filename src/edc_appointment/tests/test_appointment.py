from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from decimal import Context
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..models import Appointment
from .helper import Helper
from .models import SubjectConsent, SubjectVisit, EnrollmentOne, EnrollmentTwo
from .visit_schedule import visit_schedule1, visit_schedule2


class TestAppointment(TestCase):

    helper_cls = Helper

    def setUp(self):
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def test_appointments_creation(self):
        """Assert appointment triggering method creates appointments.
        """
        self.helper.consent_and_enroll()
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

    def test_appointments_creation2(self):
        """Asserts first appointment correctly selected if
        both visit_schedule_name and schedule_name provided.
        """
        self.helper.consent_and_enroll()
        EnrollmentTwo.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            is_eligible=True)
        self.assertEqual(Appointment.objects.all().count(), 8)

    def test_deletes_appointments(self):
        """Asserts manager method can delete appointments.
        """
        self.helper.consent_and_enroll()
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED)
        Appointment.objects.delete_for_subject_after_date(
            appointments[0].subject_identifier,
            appointments[0].appt_datetime - relativedelta(days=1))
        self.assertEqual(Appointment.objects.filter(
            subject_identifier=self.subject_identifier).count(), 1)

    def test_appointments_dates_mo(self):
        """Test appointment datetimes are chronological."""
        for index in range(0, 7):
            SubjectConsent.objects.create(
                subject_identifier=f'{self.subject_identifier}-{index}',
                consent_datetime=get_utcnow())
        for day in [MO, TU, WE, TH, FR, SA, SU]:
            subject_consent = SubjectConsent.objects.all()[day.weekday]
            EnrollmentOne.objects.create(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=(subject_consent.consent_datetime
                                 + relativedelta(weeks=2)
                                 + relativedelta(weekday=day(-1))),
                is_eligible=True)
            appt_datetimes = [
                obj.appt_datetime for obj in Appointment.objects.filter(
                    subject_identifier=subject_consent.subject_identifier).order_by(
                        'appt_datetime')]
            last = None
            self.assertGreater(len(appt_datetimes), 0)
            for appt_datetime in appt_datetimes:
                if not last:
                    last = appt_datetime
                else:
                    self.assertGreater(appt_datetime, last)
                    last = appt_datetime

    def test_timepoint(self):
        """Assert timepoints are saved from the schedule correctly
        as Decimals and ordered by appt_datetime.
        """
        context = Context(prec=2)
        self.helper.consent_and_enroll()
        self.assertEqual([obj.timepoint for obj in Appointment.objects.all().order_by('appt_datetime')],
                         [context.create_decimal(n) for n in range(0, 4)])

    def test_first_appointment_with_visit_schedule_and_schedule(self):
        """Asserts first appointment correctly selected if
        both visit_schedule_name and schedule_name provided.
        """
        self.helper.consent_and_enroll()
        subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier)
        EnrollmentTwo.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            is_eligible=True)
        enrollment_one = EnrollmentOne.objects.get(
            subject_identifier=self.subject_identifier)
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment_one.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')

        appointment = Appointment.objects.filter(
            subject_identifier=enrollment_one.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1').order_by('appt_datetime')[0]

        self.assertEqual(first_appointment, appointment)

    def test_first_appointment_with_visit_schedule(self):
        """Asserts first appointment correctly selected if just
        visit_schedule_name provided.
        """
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow())
        EnrollmentTwo.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            is_eligible=True)
        EnrollmentOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=(
                subject_consent.report_datetime + relativedelta(months=1)),
            is_eligible=True)

        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule2')
        self.assertEqual(first_appointment.schedule_name, 'schedule2')

        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_schedule_name='visit_schedule2').order_by('appt_datetime')[0],
            first_appointment)

    def test_next_appointment(self):
        self.helper.consent_and_enroll()
        enrollment = EnrollmentOne.objects.get(
            subject_identifier=self.subject_identifier)
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        next_appointment = Appointment.objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            next_appointment)

        next_appointment = Appointment.objects.next_appointment(
            appointment=first_appointment)
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            next_appointment)

    def test_next_appointment_after_last_returns_none(self):
        """Assert returns None if next after last appointment.
        """
        self.helper.consent_and_enroll()

        last_appointment = Appointment.objects.last_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        self.assertEqual(
            Appointment.objects.next_appointment(appointment=last_appointment), None)

    def test_next_appointment_until_none(self):
        """Assert can walk from first to last appointment.
        """
        self.helper.consent_and_enroll()
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        first = Appointment.objects.first_appointment(
            appointment=appointments[0])
        appts = [first]
        for appointment in appointments:
            appts.append(
                Appointment.objects.next_appointment(appointment=appointment))
        self.assertIsNotNone(appts[0])
        self.assertEqual(appts[0], first)
        self.assertEqual(appts[-1], None)

    def test_previous_appointment1(self):
        """Assert returns None if relative to first appointment."""
        self.helper.consent_and_enroll()
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        self.assertEqual(
            Appointment.objects.previous_appointment(appointment=first_appointment), None)

    def test_previous_appointment2(self):
        """Assert returns previous appointment.
        """
        self.helper.consent_and_enroll()
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        next_appointment = Appointment.objects.next_appointment(
            appointment=first_appointment)
        self.assertEqual(Appointment.objects.previous_appointment(
            appointment=next_appointment), first_appointment)

    def test_next_and_previous_appointment3(self):
        """Assert accepts appointment or indiviual attrs."""
        self.helper.consent_and_enroll()
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        next_appointment = Appointment.objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=self.subject_identifier,
            visit_schedule_name='visit_schedule1',
            schedule_name='schedule1')
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=self.subject_identifier).order_by('appt_datetime')[1],
            next_appointment)
        appointment = Appointment.objects.next_appointment(
            appointment=first_appointment)
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=self.subject_identifier).order_by('appt_datetime')[1],
            appointment)
