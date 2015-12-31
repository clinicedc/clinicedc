from django.utils import timezone

from edc_testing.models import TestVisit2
from edc_appointment.models.appointment import Appointment
from edc_constants.constants import SCHEDULED
from edc_visit_schedule.models.visit_definition import VisitDefinition
from edc_visit_tracking.models import PreviousVisitError

from .base_test import TestVisitModel, BaseTest


class TestPreviousVisitMixin(BaseTest):

    def test_previous_visit_definition(self):
        """Asserts visit definitions exist in sequence."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = False
        visit_definition = VisitDefinition.objects.get(code='2000')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = False
        test_visit = TestVisitModel.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(test_visit.previous_visit_definition(visit_definition).code, '1000')

    def test_previous_visit_doesnotexist(self):
        """Asserts the first scheduled visit has no previous visit."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = False
        self.visit_definition = VisitDefinition.objects.get(code='2000')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=self.visit_definition)
        test_visit = TestVisitModel.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertIsNone(test_visit.previous_visit())

    def test_previous_visit_exists(self):
        """Asserts that if two visits created in sequence, 1000 and 2000,
        an error is not raised when REQUIRES_PREVIOUS_VISIT is False."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = False
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        test_visit = TestVisitModel.objects.create(
            appointment=appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        visit_definition = VisitDefinition.objects.get(code='2000')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        next_test_visit = TestVisitModel.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(next_test_visit.previous_visit(), test_visit)

    def test_previous_visit(self):
        """Asserts that if two visits created in sequence, 1000 and 2000,
        an error is not raised when REQUIRES_PREVIOUS_VISIT is True."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = True
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        test_visit = TestVisitModel.objects.create(
            appointment=appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        visit_definition = VisitDefinition.objects.get(code='2000')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        next_test_visit = TestVisitModel.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(next_test_visit.previous_visit(), test_visit)

    def test_visit_raises_if_no_previous(self):
        """Asserts that the second of two visits is created first,
        an error is raised."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = True
        visit_definition = VisitDefinition.objects.get(code='2000')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        self.assertRaises(
            PreviousVisitError,
            TestVisitModel.objects.create,
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)

    def test_visit_not_raised_for_first_visit(self):
        """Asserts that if the first of two visits is created first,
        an error is not raised (this a repeat of a previous test)."""
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = True
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        with self.assertRaises(PreviousVisitError):
            try:
                TestVisitModel.objects.create(
                    appointment=appointment,
                    report_datetime=timezone.now(),
                    reason=SCHEDULED)
            except:
                pass
            else:
                raise PreviousVisitError

    def test_visit_not_raised_for_first_visit2(self):
        TestVisit2.REQUIRES_PREVIOUS_VISIT = True
        visit_definition = VisitDefinition.objects.get(code='2000A')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        with self.assertRaises(PreviousVisitError):
            try:
                TestVisit2.objects.create(
                    appointment=appointment,
                    report_datetime=timezone.now(),
                    reason=SCHEDULED)
            except Exception as e:
                raise Exception(e)
                pass
            else:
                raise PreviousVisitError

    def test_visit_raises_if_no_previous2(self):
        TestVisit2.REQUIRES_PREVIOUS_VISIT = True
        visit_definition = VisitDefinition.objects.get(code='2010A')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        self.assertRaises(
            PreviousVisitError,
            TestVisit2.objects.create,
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)

    def test_previous_visit_definition2(self):
        TestVisit2.REQUIRES_PREVIOUS_VISIT = False
        visit_definition = VisitDefinition.objects.get(code='2010A')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisit2.REQUIRES_PREVIOUS_VISIT = False
        test_visit = TestVisit2.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(test_visit.previous_visit_definition(visit_definition).code, '2000A')

    def test_previous_visit_definition2A(self):
        TestVisit2.REQUIRES_PREVIOUS_VISIT = False
        visit_definition = VisitDefinition.objects.get(code='2020A')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisit2.REQUIRES_PREVIOUS_VISIT = False
        test_visit = TestVisit2.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(test_visit.previous_visit_definition(visit_definition).code, '2010A')

    def test_previous_visit_definition2B(self):
        TestVisitModel.REQUIRES_PREVIOUS_VISIT = False
        visit_definition = VisitDefinition.objects.get(code='2030A')
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisit2.REQUIRES_PREVIOUS_VISIT = False
        test_visit = TestVisit2.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(test_visit.previous_visit_definition(visit_definition).code, '2020A')
