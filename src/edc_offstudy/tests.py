from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from django.utils import timezone
from django.test import TestCase

from edc_constants.constants import DEAD, OFF_STUDY
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory
from edc_example.models import CrfOne, SubjectOffstudy
from edc_example.models import SubjectVisit, Appointment, Enrollment, CrfTwo
from edc_metadata.constants import KEYED, NOT_REQUIRED
from edc_visit_tracking.constants import SCHEDULED, LOST_VISIT, COMPLETED_PROTOCOL_VISIT

from .model_mixins import OffstudyError


class TestOffstudy(TestCase):

    def setUp(self):
        self.subject_identifier = '111111111'
        self.subject_consent = SubjectConsentFactory(
            subject_identifier=self.subject_identifier,
            consent_datetime=timezone.now() - relativedelta(weeks=4))
        Enrollment.objects.create(subject_identifier=self.subject_consent.subject_identifier)

    def test_off_study_date_after_consent(self):
        """Assert can go off study a week after consent."""
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=timezone.now() - relativedelta(weeks=3),
                reason=DEAD
            )
        except OffstudyError as e:
            self.fail(str(e))

    def test_off_study_date_before_consent(self):
        """Assert cannot go off study a week before consent."""
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=timezone.now() - relativedelta(weeks=5),
                reason=DEAD
            )
            self.fail('OffstudyError not raised')
        except OffstudyError:
            pass

    def test_off_study_date_before_subject_visit(self):
        """Assert cannot enter off study if visits already exist after offstudy date."""
        appointment = Appointment.objects.filter(visit_schedule_name=SubjectOffstudy._meta.visit_schedule_name).first()
        self.subject_visit = SubjectVisitFactory(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=timezone.now(),
            study_status=SCHEDULED
        )
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=timezone.now() - relativedelta(weeks=3),
                reason=DEAD
            )
            self.fail('OffstudyError not raised')
        except OffstudyError:
            pass

    def test_off_study_date_after_subject_visit(self):
        """Assert can enter off study if visits do not exist after offstudy date."""
        appointment = Appointment.objects.filter(visit_schedule_name=SubjectOffstudy._meta.visit_schedule_name).first()
        self.subject_visit = SubjectVisitFactory(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=timezone.now() - relativedelta(weeks=1),
            study_status=SCHEDULED
        )
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=timezone.now(),
                reason=DEAD
            )
        except OffstudyError:
            self.fail('OffstudyError unexpectedly raised')
