from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from edc_appointment.models import Appointment
from edc_constants.constants import SCHEDULED
from edc_offstudy.constants import OFF_STUDY_REASONS
from edc_offstudy.models import OffStudyError
from edc_offstudy.tests.base_test import BaseTest
from edc_offstudy.tests.test_models import TestVisitModel, TestOffStudyModel, AnotherTestVisitModel
from edc_visit_schedule.models import VisitDefinition


class TestOffStudy(BaseTest):

    def test_visit_knows_offstudy_model_as_class(self):
        test_visit = AnotherTestVisitModel(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(test_visit.off_study_model, TestOffStudyModel)

    def test_visit_knows_offstudy_model_from_tuple(self):
        test_visit = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now())
        self.assertEqual(test_visit.off_study_model, TestOffStudyModel)

    def test_offstudy_knows_visit_model(self):
        self.assertEqual(TestOffStudyModel.visit_model, TestVisitModel)

    def test_offstudy_knows_visit_model_attr(self):
        self.assertEqual(TestOffStudyModel.visit_model_attr, 'test_visit_model')

    def test_off_study_report_blocks_future_visits_on_reason_only(self):
        for reason in OFF_STUDY_REASONS:
            visit_definition = VisitDefinition.objects.get(code='1000')
            appointment = Appointment.objects.get(
                registered_subject=self.registered_subject,
                visit_definition=visit_definition)
            test_visit = TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                reason=reason)
            visit_definition = VisitDefinition.objects.get(code='2000')
            appointment = Appointment.objects.get(
                registered_subject=self.registered_subject,
                visit_definition=visit_definition)
            with self.assertRaises(OffStudyError) as cm:
                TestVisitModel.objects.create(
                    appointment=appointment,
                    report_datetime=timezone.now(),
                    reason=SCHEDULED)
            self.assertIn(
                'On a previous visit participant was meant to go off study (reason={})'.format(reason),
                str(cm.exception))
            test_visit.delete()

    def test_off_study_report_blocks_future_visits_by_off_study_report_not_reason(self):
        visit_definition = VisitDefinition.objects.get(code='1000')
        for reason in OFF_STUDY_REASONS:
            test_visit_model = TestVisitModel.objects.create(
                appointment=self.appointment,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                reason=reason)
            test_off_study = TestOffStudyModel.objects.create(
                test_visit_model=test_visit_model,
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
            test_off_study.delete()
            test_visit_model.delete()

    def test_blocks_off_study_report_if_visit_reason_not_off_study(self):
        test_visit_model = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        with self.assertRaises(OffStudyError) as cm:
            TestOffStudyModel.objects.create(
                test_visit_model=test_visit_model,
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
        for reason in OFF_STUDY_REASONS:
            test_visit_model = TestVisitModel.objects.create(
                appointment=appointment,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                reason=reason)
            test_off_study = TestOffStudyModel.objects.create(
                test_visit_model=test_visit_model,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                offstudy_date=date.today())
            self.assertEqual(
                Appointment.objects.filter(registered_subject=self.registered_subject).count(), 2)
            self.assertTrue(
                Appointment.objects.filter(
                    registered_subject=self.registered_subject).order_by('appt_datetime').last().appt_datetime -
                appt_datetime < timedelta(days=1))
            test_off_study.delete()
            test_visit_model.delete()

    def test_can_edit_visit_before_off_study_report(self):
        visit_definition = VisitDefinition.objects.get(code='2000')
        previous_test_visit = TestVisitModel.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        next_appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        for reason in OFF_STUDY_REASONS:
            test_visit_model = TestVisitModel.objects.create(
                appointment=next_appointment,
                report_datetime=timezone.now(),
                reason=reason)
            test_off_study = TestOffStudyModel.objects.create(
                test_visit_model=test_visit_model,
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
            test_off_study.delete()
            test_visit_model.delete()
