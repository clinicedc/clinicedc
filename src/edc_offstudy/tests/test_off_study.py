from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone

from edc.subject.registration.models import RegisteredSubject
from edc.subject.visit_schedule.models import VisitDefinition
from edc_appointment.models import Appointment
from edc_base.model.models import BaseUuidModel
from edc_constants.constants import SCHEDULED, OFF_STUDY
from edc_offstudy.models import OffStudyModelMixin, OffStudyError
from edc_offstudy.tests.base_test import BaseTest, TestVisitModel


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
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisitModel.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        visit_definition = VisitDefinition.objects.get(code='2000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        with self.assertRaises(OffStudyError) as cm:
            TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now(),
                reason=SCHEDULED)
        self.assertIn('On a previous visit participant was meant to go off study', str(cm.exception))

    def test_off_study_report_blocks_future_visits_by_off_study_report_not_reason(self):
        visit_definition = VisitDefinition.objects.get(code='1000')
        TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3))
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
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
        self.assertIn('Off study report must be submitted with an '
                      'off study visit on the same day.', str(cm.exception))

    def test_off_study_deletes_future_appointments(self):
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        TestVisitModel.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        visit_definition = VisitDefinition.objects.get(code='2000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        appt_datetime = appointment.appt_datetime
        self.assertLess(appt_datetime, timezone.now())
        TestVisitModel.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=OFF_STUDY)
        TestOffStudyModel.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today())
        self.assertEqual(
            Appointment.objects.filter(registered_subject=self.registered_subject).count(), 2)
        self.assertTrue(
            Appointment.objects.filter(
                registered_subject=self.registered_subject).order_by('appt_datetime').last().appt_datetime -
            appt_datetime < timedelta(days=1))

    def test_can_edit_visit_before_off_study_report(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        previous_test_visit = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
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
