from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.model_mixins import PreviousVisitError
from edc_visit_tracking.visit_sequence import VisitSequence, VisitSequenceError

from ..helper import Helper
from ..models import SubjectVisit
from ..visit_schedule import visit_schedule1, visit_schedule2


class DisabledVisitSequence(VisitSequence):
    def enforce_sequence(self):
        return None


class TestPreviousVisit(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        SubjectVisit.visit_sequence_cls = VisitSequence
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "edc_visit_tracking.subjectvisit"
            }
        )
        self.helper.consent_and_put_on_schedule()

    def tearDown(self):
        SubjectVisit.visit_sequence_cls = VisitSequence

    def test_visit_sequence_enforcer_on_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED,
        )
        visit_sequence = VisitSequence(appointment=visit.appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            self.fail(f"VisitSequenceError unexpectedly raised. Got '{e}'")

    def test_visit_sequence_enforcer_without_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED,
        )
        visit_sequence = VisitSequence(appointment=visit.appointment)
        self.assertRaises(VisitSequenceError, visit_sequence.enforce_sequence)

    def test_requires_previous_visit_thru_model(self):
        """Asserts requires previous visit to exist on create.
        """
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED,
        )
        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED,
        )
        SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED,
        )
        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[3],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED,
        )

    def test_requires_previous_visit_thru_model2(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        opts = appointments[1].__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")

        opts["visit_code_sequence"] = 1
        Appointment.objects.create(**opts)
        opts["visit_code_sequence"] = 2

        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED,
        )

        self.assertRaises(
            PreviousVisitError,
            SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() - relativedelta(months=8),
        )

    def test_previous_appointment(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        visit_sequence = VisitSequence(appointment=appointments[0])
        self.assertIsNone(visit_sequence.previous_appointment)
        visit_sequence = VisitSequence(appointment=appointments[1])
        self.assertEqual(visit_sequence.previous_appointment, appointments[0])
        visit_sequence = VisitSequence(appointment=appointments[2])
        self.assertEqual(visit_sequence.previous_appointment, appointments[1])

    def test_previous_appointment_with_unscheduled(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        # insert some unscheduled appointments
        opts = appointments[1].__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        Appointment.objects.create(**opts)
        opts["visit_code_sequence"] = 2
        Appointment.objects.create(**opts)

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

    def test_previous_appointment_broken_sequence2(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )

        opts = appointments[1].__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 2
        Appointment.objects.create(**opts)

        visit_sequence = VisitSequence(appointment=appointments[0])
        self.assertIsNone(visit_sequence.previous_appointment)
        visit_sequence = VisitSequence(appointment=appointments[1])
        self.assertEqual(visit_sequence.previous_appointment, appointments[0])

        visit_sequence = VisitSequence(appointment=appointments[2])
        self.assertRaises(
            VisitSequenceError, getattr, visit_sequence, "previous_appointment"
        )

        visit_sequence = VisitSequence(appointment=appointments[3])
        self.assertEqual(visit_sequence.previous_appointment, appointments[2])

    def test_previous_visit(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED,
            )

    def test_previous_visit2(self):
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        opts = appointments[1].__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts["visit_code_sequence"] = 1
        Appointment.objects.create(**opts)
        opts["visit_code_sequence"] = 2
        Appointment.objects.create(**opts)

        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED
                if appointment.visit_code_sequence == 0
                else UNSCHEDULED,
            )
