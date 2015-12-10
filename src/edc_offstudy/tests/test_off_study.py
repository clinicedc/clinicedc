from datetime import date
from django.db import models

from edc_offstudy.models import OffStudyModelMixin, OffStudyMixin
from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc.subject.registration.models import RegisteredSubject
from edc.subject.visit_tracking.models.base_visit_tracking import BaseVisitTracking
from edc.entry_meta_data.models.meta_data_mixin import MetaDataMixin
from edc.subject.visit_tracking.models.previous_visit_mixin import PreviousVisitMixin
from edc_offstudy.tests.base_test import BaseTest
from django.utils import timezone
from edc_offstudy.models.off_study_model_mixin import OffStudyError
from dateutil.relativedelta import relativedelta
from edc.subject.appointment.models.appointment import Appointment
from edc.subject.visit_schedule.models.visit_definition import VisitDefinition
from edc_constants.constants import SCHEDULED, OFF_STUDY


class TestVisitModel(OffStudyMixin, MetaDataMixin, PreviousVisitMixin, BaseVisitTracking):

    OFF_STUDY_MODEL = ('edc_offstudy', 'TestOffStudyModel')
    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'


class TestOffStudyModel(OffStudyModelMixin, BaseUuidModel):

    VISIT_MODEL = TestVisitModel

    registered_subject = models.OneToOneField(RegisteredSubject)

    class Meta:
        app_label = 'edc_offstudy'


class TestOffStudy(BaseTest):

    def test_visit_knows_offstudy_model(self):
        test_visit = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertIs(test_visit.OFF_STUDY_MODEL, TestOffStudyModel)

    def test_offstudy_knows_visit_mode(self):
        self.assertIs(TestOffStudyModel.VISIT_MODEL, TestVisitModel)

    def test_off_study_report_blocks_future_visits_on_reason_only(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        appointment = Appointment.objects.create(
            registered_subject=self.registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        with self.assertRaises(OffStudyError) as cm:
            TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now())
        self.assertIn('On a previous visit participant was meant to go off study', str(cm.exception))

    def test_off_study_report_blocks_future_visits_on_reason2(self):
        """Asserts that if visit and off study date are on the same day it will
        not block entry because of that."""
        visit_definition = VisitDefinition.objects.get(code='2000')
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today())  # this is a future date?
        appointment = Appointment.objects.create(
            registered_subject=self.registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        with self.assertRaises(OffStudyError) as cm:
            TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now())
        self.assertIn('On a previous visit participant was meant to go off study', str(cm.exception))

    def test_off_study_report_blocks_future_visits_by_off_study_report_not_reason(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3))
        appointment = Appointment.objects.create(
            registered_subject=self.registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        with self.assertRaises(OffStudyError) as cm:
            TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now())
        self.assertIn('Participant was reported off study on', str(cm.exception))

    def test_blocks_off_study_report_if_visit_reason_not_off_study(self):
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        with self.assertRaises(OffStudyError) as cm:
            TestOffStudyModel.objects.create(
                registered_subject=self.registered_subject,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                offstudy_date=date.today() - relativedelta(weeks=4))
        self.assertIn('Off study report must be submitted on an off study visit', str(cm.exception))

    def test_off_study_deletes_future_appointments(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        appt_datetime = Appointment.objects.get(registered_subject=self.registered_subject).appt_datetime
        self.assertLess(appt_datetime, timezone.now())
        Appointment.objects.create(
            registered_subject=self.registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        self.assertEqual(
            Appointment.objects.filter(registered_subject=self.registered_subject).count(), 2)
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today())
        self.assertEqual(
            Appointment.objects.filter(registered_subject=self.registered_subject).count(), 1)
        self.assertEqual(
            Appointment.objects.get(registered_subject=self.registered_subject).appt_datetime,
            appt_datetime)

    def test_can_edit_visit_before_off_study_report(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        previous_test_visit = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        next_appointment = Appointment.objects.create(
            registered_subject=self.registered_subject,
            appt_datetime=timezone.now(),
            visit_definition=visit_definition)
        TestVisitModel.objects.create(
            appointment=next_appointment,
            report_datetime=timezone.now(),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now(),
            offstudy_date=date.today())
        with self.assertRaises(OffStudyError):
            try:
                previous_test_visit.report_datetime = timezone.now() - relativedelta(weeks=5)
                previous_test_visit.save()
            except:
                pass
            else:
                raise OffStudyError
