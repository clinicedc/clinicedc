from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from django.utils import timezone


from django.test.testcases import TestCase

from edc_example.models import (
    SubjectVisit, Appointment, Enrollment)
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory


from edc_constants.constants import ON_STUDY, OFF_STUDY
from edc_offstudy.constants import OFF_STUDY_REASONS
from edc_example.models import CrfOffStudy

from edc_visit_tracking.constants import SCHEDULED
from edc_offstudy.model_mixins import OffStudyError


class TestOffStudy(TestCase):

    def test_visit_knows_offstudy_model_as_class(self):
        test_visit = SubjectVisit(
            report_datetime=timezone.now())
        self.assertEqual(test_visit.offstudy, CrfOffStudy)

    def test_visit_knows_offstudy_model_from_tuple(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisitFactory(appointment=appointment)
        self.assertEqual(subject_visit.offstudy, CrfOffStudy)

    def test_offstudy_knows_visit_model(self):
        self.assertEqual(CrfOffStudy.visit_model, SubjectVisit)

    def test_offstudy_knows_visit_model_attr(self):
        self.assertEqual(CrfOffStudy.visit_model_attr(), 'subject_visit')

    def test_off_study_report_blocks_future_visits(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.get(
            visit_code='1000'
        )
        SubjectVisitFactory(
            appointment=appointment,
            visit_schedule_name='subject_visit_schedule',
            schedule_name='schedule-1',
            report_datetime=timezone.now() - relativedelta(weeks=4),
            study_status=OFF_STUDY
        )
        appointment = Appointment.objects.get(
            visit_code='2000'
        )
        with self.assertRaises(OffStudyError) as cm:
            SubjectVisitFactory(
                appointment=appointment,
                visit_schedule_name='subject_visit_schedule',
                subject_identifier=appointment.subject_identifier,
                schedule_name='schedule-1',
            )
        error_msg = str(cm.exception)
        self.assertTrue(
            error_msg.startswith('On a previous visit participant was meant to go off study'))

    def test_off_study_report_blocks_future_visits_by_off_study_report_not_reason(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.get(
            visit_code='1000'
        )
        for reason in OFF_STUDY_REASONS:
            test_visit_model = SubjectVisit.objects.create(
                appointment=appointment,
                study_status=OFF_STUDY,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                reason=reason)

            test_off_study = CrfOffStudy.objects.create(
                subject_visit=test_visit_model,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                offstudy_date=date.today() - relativedelta(weeks=3)
            )

            with self.assertRaises(OffStudyError) as cm:
                SubjectVisit.objects.create(
                    appointment=appointment,
                    report_datetime=timezone.now())
            self.assertIn('Participant was reported off study on', str(cm.exception))
            test_off_study.delete()
            test_visit_model.delete()

    def test_blocks_off_study_report_if_study_status_not_off_study(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.get(
            visit_code='1000'
        )
        test_visit_model = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            study_status=ON_STUDY,
            reason=SCHEDULED)
        with self.assertRaises(OffStudyError) as cm:
            CrfOffStudy.objects.create(
                subject_visit=test_visit_model,
                report_datetime=timezone.now() - relativedelta(weeks=4),
                offstudy_date=date.today() - relativedelta(weeks=4))
        self.assertIn(
            'Off study report must be submitted with a visit report on the same day with study_status '
            'set to \'off study\'. Using off study report date {}.'.format(
                (timezone.now() - relativedelta(weeks=4)).strftime('%Y-%m-%d')), str(cm.exception))

    def test_off_study_deletes_future_appointments(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.get(
            visit_code='1000',
            subject_identifier=subject_consent.subject_identifier
        )
        SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)

        appointment = Appointment.objects.get(
            visit_code='2000',
            subject_identifier=subject_consent.subject_identifier
        )
        appt_datetime = appointment.appt_datetime
        self.assertLess(appt_datetime, timezone.now())

        for reason in OFF_STUDY_REASONS:
            test_visit_model = SubjectVisitFactory(
                appointment=appointment,
                visit_schedule_name='subject_visit_schedule',
                subject_identifier=appointment.subject_identifier,
                schedule_name='schedule-1',
                report_datetime=timezone.now() - relativedelta(weeks=2),
                study_status=OFF_STUDY,
                reason=reason
            )
            test_off_study = CrfOffStudy.objects.create(
                subject_visit=test_visit_model,
                report_datetime=timezone.now() - relativedelta(weeks=2),
                offstudy_date=date.today())

            self.assertEqual(
                Appointment.objects.filter(subject_identifier=subject_consent.subject_identifier).count(), 2)
            self.assertTrue(
                Appointment.objects.filter(
                    subject_identifier=subject_consent.subject_identifier).order_by('appt_datetime').last().appt_datetime -
                appt_datetime < timedelta(days=1))
            test_off_study.delete()
            test_visit_model.delete()

    def test_can_edit_visit_before_off_study_report(self):
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.get(
            visit_code='1000',
            subject_identifier=subject_consent.subject_identifier
        )
        previous_test_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            reason=SCHEDULED)
        next_appointment = Appointment.objects.get(
            subject_identifier=subject_consent.subject_identifier,
            visit_code='2000')
        for reason in OFF_STUDY_REASONS:
            test_visit_model = SubjectVisit.objects.create(
                appointment=next_appointment,
                report_datetime=timezone.now(),
                study_status=OFF_STUDY,
                reason=reason)
            test_off_study = CrfOffStudy.objects.create(
                subject_visit=test_visit_model,
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
