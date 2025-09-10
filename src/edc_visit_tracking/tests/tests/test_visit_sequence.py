from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.models import Appointment
from edc_appointment.utils import reset_appointment, skip_appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.model_mixins import PreviousVisitError
from edc_visit_tracking.models import SubjectVisit
from edc_visit_tracking.visit_sequence import VisitSequence, VisitSequenceError
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule

from ..crfs import crfs
from ..requisitions import requisitions

utc_tz = ZoneInfo("UTC")


@tag("visit_tracking")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestPreviousVisit(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        visit_schedule1 = get_visit_schedule(
            consent_v1,
            crfs=crfs,
            requisitions=requisitions,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            onschedule_model="clinicedc_tests.onscheduleone",
            offschedule_model="clinicedc_tests.offscheduleone",
            visit_count=4,
            allow_unscheduled=True,
        )
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        visit_schedule2 = get_visit_schedule(
            consent_v1,
            crfs=crfs,
            requisitions=requisitions,
            visit_schedule_name="visit_schedule2",
            schedule_name="schedule2",
            onschedule_model="clinicedc_tests.onscheduletwo",
            offschedule_model="clinicedc_tests.offscheduletwo",
            visit_count=4,
            allow_unscheduled=True,
        )
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def setUp(self):
        self.helper = self.helper_cls()
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            consent_definition=consent_v1,
        )
        self.subject_identifier = subject_consent.subject_identifier

    def test_visit_sequence_enforcer_on_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow(),
            reason=SCHEDULED,
        )
        visit_sequence = VisitSequence(appointment=appointments[1])
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            self.fail(f"VisitSequenceError unexpectedly raised. Got '{e}'")

    def test_visit_sequence_enforcer_without_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        visit_sequence = VisitSequence(appointment=appointments[1])
        self.assertRaises(VisitSequenceError, visit_sequence.enforce_sequence)

    def test_requires_previous_visit_thru_model(self):
        """Asserts requires previous visit to exist on create."""
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow(),
            reason=SCHEDULED,
        )
        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() + relativedelta(months=2),
            reason=SCHEDULED,
        )
        SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() + relativedelta(months=1),
            reason=SCHEDULED,
        )
        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[3],
            report_datetime=get_utcnow() + relativedelta(months=3),
            reason=SCHEDULED,
        )

    def test_requires_previous_visit_thru_model2(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow(),
            reason=SCHEDULED,
        )

        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() + relativedelta(months=2),
        )

    def test_previous_appointment(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        visit_sequence = VisitSequence(appointment=appointments[0], skip_enforce=True)
        self.assertIsNone(visit_sequence.previous_appointment)
        visit_sequence = VisitSequence(appointment=appointments[1], skip_enforce=True)
        self.assertEqual(visit_sequence.previous_appointment, appointments[0])
        visit_sequence = VisitSequence(appointment=appointments[2], skip_enforce=True)
        self.assertEqual(visit_sequence.previous_appointment, appointments[1])

    def test_previous_appointment_with_unscheduled(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() + relativedelta(months=index),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

            unscheduled_appointment = self.helper.add_unscheduled_appointment(
                appointment
            )
            SubjectVisit.objects.create(
                appointment=unscheduled_appointment,
                report_datetime=get_utcnow()
                + relativedelta(months=index)
                + relativedelta(days=1),
                reason=UNSCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        visit_sequence = VisitSequence(appointment=appointments[0])
        self.assertIsNone(visit_sequence.previous_appointment)
        for i in range(0, Appointment.objects.all().count() - 1):
            visit_sequence = VisitSequence(appointment=appointments[i + 1])
            self.assertEqual(visit_sequence.previous_appointment, appointments[i])

    def test_previous_appointment_broken_sequence1(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        self.assertRaises(AppointmentDeleteError, appointments[1].delete)

    def test_previous_visit_report_broken_sequence2(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() + relativedelta(months=index),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

            unscheduled_appointment = self.helper.add_unscheduled_appointment(
                appointment
            )
            SubjectVisit.objects.create(
                appointment=unscheduled_appointment,
                report_datetime=get_utcnow()
                + relativedelta(months=index)
                + relativedelta(days=1),
                reason=UNSCHEDULED,
            )
            unscheduled_appointment.appt_status = INCOMPLETE_APPT
            unscheduled_appointment.save()

            unscheduled_appointment = self.helper.add_unscheduled_appointment(
                appointment,
                suggested_appt_datetime=get_utcnow()
                + relativedelta(months=index)
                + relativedelta(days=2),
            )
            SubjectVisit.objects.create(
                appointment=unscheduled_appointment,
                report_datetime=get_utcnow()
                + relativedelta(months=index)
                + relativedelta(days=2),
                reason=UNSCHEDULED,
            )
            unscheduled_appointment.appt_status = INCOMPLETE_APPT
            unscheduled_appointment.save()

        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        visit_sequence = VisitSequence(appointment=appointments[0])  # 1000.0
        self.assertIsNone(visit_sequence.previous_appointment)
        visit_sequence = VisitSequence(appointment=appointments[1])  # 1000.1
        self.assertEqual(visit_sequence.previous_appointment, appointments[0])  # 1000.0

        appointments[1].related_visit.delete()

        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        visit_sequence = VisitSequence(appointment=appointments[2])  # 1000.2
        self.assertRaises(VisitSequenceError, visit_sequence.enforce_sequence)

        visit_sequence = VisitSequence(appointment=appointments[3])
        self.assertRaises(
            VisitSequenceError, getattr, visit_sequence, "previous_appointment"
        )

    def test_previous_visit(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() + relativedelta(months=index),
                reason=SCHEDULED,
            )

    def test_previous_visit_with_inserted_unscheduled(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() + relativedelta(months=index),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()
            unscheduled_appointment = self.helper.add_unscheduled_appointment(
                appointment
            )
            SubjectVisit.objects.create(
                appointment=unscheduled_appointment,
                report_datetime=get_utcnow()
                + relativedelta(months=index)
                + relativedelta(days=1),
                reason=UNSCHEDULED,
            )
            unscheduled_appointment.appt_status = INCOMPLETE_APPT
            unscheduled_appointment.save()

    def test_requires_previous_visit_unless_skipped(self):
        """Asserts does not require previous visit if previous appt
        is skipped.
        """
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow(),
            reason=SCHEDULED,
        )

        skip_appointment(appointments[1])

        try:
            SubjectVisit.objects.create(
                appointment=appointments[2],
                report_datetime=get_utcnow() + relativedelta(months=2),
                reason=SCHEDULED,
            )
        except PreviousVisitError:
            self.fail("PreviousVisitError unexpectedly raised.")

        reset_appointment(appointments[1])

        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() + relativedelta(months=2),
            reason=SCHEDULED,
        )
