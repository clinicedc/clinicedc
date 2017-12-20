from django.test import TestCase, tag
from uuid import uuid4

from ..enroll_to_schedule import EnrollToSchedule, EnrollToScheduleError
from ..enrolled_subject import EnrolledSubject
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..visit_schedule import VisitSchedule
from .models import EnrollmentTwo, SubjectConsent


class TestEnrolledSubject(TestCase):

    def setUp(self):
        site_visit_schedules._registry = {}
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport',
            enrollment_model='edc_visit_schedule.Enrollment',
            disenrollment_model='edc_visit_schedule.Disenrollment')

        self.schedule = Schedule(
            name='schedule',
            enrollment_model='edc_visit_schedule.Enrollment',
            disenrollment_model='edc_visit_schedule.Disenrollment')
        self.schedule3 = Schedule(
            name='schedule_three',
            enrollment_model='edc_visit_schedule.EnrollmentThree',
            disenrollment_model='edc_visit_schedule.DisenrollmentThree')

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules.register(self.visit_schedule)

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport')

        self.schedule_two_1 = Schedule(
            name='schedule_two',
            enrollment_model='edc_visit_schedule.EnrollmentTwo',
            disenrollment_model='edc_visit_schedule.DisenrollmentTwo')
        self.schedule_two_2 = Schedule(
            name='schedule_four',
            enrollment_model='edc_visit_schedule.EnrollmentFour',
            disenrollment_model='edc_visit_schedule.DisenrollmentFour')

        self.visit_schedule_two.add_schedule(self.schedule_two_1)
        self.visit_schedule_two.add_schedule(self.schedule_two_2)
        site_visit_schedules.register(self.visit_schedule_two)
        self.subject_identifier = '111111'
        obj = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier)
        self.consent_identifier = obj.consent_identifier

    def test_enrolled_subject(self):
        enrolled_subject = EnrolledSubject()
        self.assertFalse(enrolled_subject.enrollments)

    def test_enrolled_subject_not_enrolled(self):
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertFalse(enrolled_subject.enrollments)

    def test_get_enrollment_not_enrolled(self):
        """Asserts returns an empty list if not enrolled.
        """
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertFalse(enrolled_subject.enrollments)

    def test_get_enrollment_enrolled(self):
        """Asserts returns an enrollment instance if enrolled.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model_cls=EnrollmentTwo,
            subject_identifier=self.subject_identifier,
            consent_identifier=uuid4(),
            eligible=True)
        obj = enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            enrolled_subject.enrollments, [obj])

    def test_get_enrollment_enrolled_many(self):
        """Asserts returns an empty list if not enrolled.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        obj1 = enroll_to_schedule.enroll()
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmentfour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        obj2 = enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertEqual(enrolled_subject.enrollments, [obj1, obj2])

    def test_schedules(self):
        """Asserts returns one schedule if one enrollment.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            [s.name for s in enrolled_subject.schedules.values()],
            ['schedule_two'])

    def test_schedules_many(self):
        """Asserts returns two schedules if two enrollments.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmentfour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            [s.name for s in enrolled_subject.schedules.values()],
            ['schedule_four', 'schedule_two'])

    def test_gets_correct_enrollments_if_many_others(self):
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        obj = enroll_to_schedule.enroll()
        for i in range(0, 5):
            SubjectConsent.objects.create(subject_identifier=str(i))
            EnrollToSchedule(
                enrollment_model='edc_visit_schedule.enrollmentfour',
                subject_identifier=str(i),
                consent_identifier=uuid4(),
                eligible=True)
            enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier)
        self.assertEqual(enrolled_subject.enrollments, [obj])

    def test_get_enrollment_enrolled5(self):
        """Asserts returns None for unknown schedule.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmentfour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        self.assertRaises(
            SiteVisitScheduleError,
            EnrolledSubject,
            subject_identifier=self.subject_identifier,
            visit_schedule_name='blah')

    def test_get_enrollment_enrolled6(self):
        """Asserts returns the correct instances for the schedule.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmentfour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier,
            schedule_name='schedule_four')
        self.assertEqual(len(enrolled_subject.enrollments), 1)

    def test_raises_if_no_consent(self):
        """Asserts raises if no consent for this subject.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier='ABCDEF',
            consent_identifier=uuid4(),
            eligible=True)
        self.assertRaises(
            EnrollToScheduleError,
            enroll_to_schedule.enroll)

    def test_multpile_consents(self):
        """Asserts does not raise if more than one consent
        for this subject
        """

        subject_identifier = 'ABCDEF'
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            version='1')
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            version='2')
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=subject_identifier,
            consent_identifier=uuid4(),
            eligible=True)
        try:
            enroll_to_schedule.enroll()
        except EnrollToScheduleError:
            self.fail('EnrollToScheduleError unexpectedly raised.')

    def test_update(self):
        """Asserts returns the correct instances for the schedule.
        """
        enroll_to_schedule = EnrollToSchedule(
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
        enroll_to_schedule.enroll()
        enroll_to_schedule.update()

    def test_enroll_on_schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name='visit_schedule')
        schedule = visit_schedule.schedules.get('schedule')
        schedule.enroll(
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier,
            eligible=True)
