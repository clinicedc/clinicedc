from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from django.utils import timezone


from django.test.testcases import TestCase

from edc_example.models import (
    SubjectVisit, Appointment, Enrollment, CrfTwo)
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory

from edc_constants.constants import DEAD, OFF_STUDY
from edc_example.models import CrfOne, SubjectOffstudy

from edc_visit_tracking.constants import SCHEDULED, LOST_VISIT, COMPLETED_PROTOCOL_VISIT
from edc_offstudy.model_mixins import OffstudyError
from edc_metadata.constants import KEYED, NOT_REQUIRED


class TestOffstudy(TestCase):

    def setUp(self):
        self.subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=self.subject_consent.subject_identifier)
        self.appointment = Appointment.objects.get(
            visit_code='1000'
        )
        self.subject_visit = SubjectVisitFactory(
            appointment=self.appointment,
            visit_schedule_name='subject_visit_schedule',
            schedule_name='schedule-1',
            report_datetime=timezone.now(),
            study_status=SCHEDULED
        )

    def test_is_offstudy_or_raise(self):
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_date=date.today() - relativedelta(weeks=3),
            reason=DEAD
        )
        with self.assertRaises(OffstudyError) as cm:
            CrfOne.objects.create(
                subject_visit=self.subject_visit
            )
        self.assertIn('Participant was reported off study on', str(cm.exception))

    def test_is_offstudy_or_raise_new_visits(self):
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_date=date.today() - relativedelta(weeks=3),
        )
        with self.assertRaises(OffstudyError) as cm:
            SubjectVisit.objects.create(
                appointment=self.appointment,
                report_datetime=timezone.now())
        self.assertIn('Participant was reported off study on', str(cm.exception))

    def test_offstudy_on_delete_future_appts(self):
        self.assertEqual(1, Appointment.objects.all().count())
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_date=timezone.now(),
            reason=DEAD,
        )
        self.assertEqual(1, Appointment.objects.all().count())

    def test_offstudy_on_delete_future_appts1(self):
        appointment = Appointment.objects.get(
            visit_code='2000'
        )
        SubjectVisitFactory(
            appointment=appointment,
            visit_schedule_name='subject_visit_schedule',
            schedule_name='schedule-1',
            report_datetime=timezone.now() - relativedelta(weeks=3),
            study_status=SCHEDULED
        )
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_date=date.today() - relativedelta(weeks=3),
            reason=DEAD,
        )
        self.assertEqual(2, Appointment.objects.all().count())
