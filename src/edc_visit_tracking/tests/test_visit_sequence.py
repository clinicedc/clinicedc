from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from ..constants import SCHEDULED
from ..exceptions import PreviousVisitError

from .models import SubjectVisit
from .helper import Helper
from .visit_schedule import visit_schedule1, visit_schedule2
from ..visit_sequence import VisitSequence, VisitSequenceError


class DisabledVisitSequence(VisitSequence):
    def enforce_sequence(self):
        return None


class TestPreviousVisit(TestCase):

    helper_cls = Helper

    def setUp(self):
        SubjectVisit.visit_sequence_cls = VisitSequence
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper.consent_and_enroll()

    def tearDown(self):
        SubjectVisit.visit_sequence_cls = VisitSequence

    def test_visit_sequence_enforcer_on_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by('timepoint_datetime')
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        visit_sequence = VisitSequence(appointment=visit.appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            self.fail(f'VisitSequenceError unexpectedly raised. Got \'{e}\'')

    def test_visit_sequence_enforcer_without_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by('timepoint_datetime')
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        visit_sequence = VisitSequence(appointment=visit.appointment)
        self.assertRaises(VisitSequenceError, visit_sequence.enforce_sequence)

    def test_requires_previous_visit_thru_model(self):
        """Asserts requires previous visit to exist on create.
        """
        appointments = Appointment.objects.all().order_by('timepoint_datetime')
        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        self.assertRaises(
            PreviousVisitError, SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED)
        SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        self.assertRaises(
            PreviousVisitError, SubjectVisit.objects.create,
            appointment=appointments[3],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED)
