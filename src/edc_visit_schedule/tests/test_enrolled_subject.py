from django.test import TestCase, tag

from ..enrolled_subject import EnrolledSubject
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..visit_schedule import VisitSchedule
from .models import SubjectVisit, SubjectOffstudy, DeathReport, Disenrollment, DisenrollmentThree
from .models import Enrollment, EnrollmentTwo, EnrollmentThree, DisenrollmentTwo, EnrollmentFour, DisenrollmentFour


@tag('enroll')
class TestEnrolledSubject(TestCase):
    def setUp(self):
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport,
            enrollment_model=Enrollment,
            disenrollment_model=Disenrollment)

        self.schedule = Schedule(
            name='schedule',
            enrollment_model=Enrollment._meta.label_lower,
            disenrollment_model=Disenrollment._meta.label_lower)
        self.schedule3 = Schedule(
            name='schedule_three',
            enrollment_model=EnrollmentThree._meta.label_lower,
            disenrollment_model=DisenrollmentThree._meta.label_lower)

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport)

        self.schedule_two_1 = Schedule(
            name='schedule_two',
            enrollment_model=EnrollmentTwo._meta.label_lower,
            disenrollment_model=DisenrollmentTwo._meta.label_lower)
        self.schedule_two_2 = Schedule(
            name='schedule_four',
            enrollment_model=EnrollmentFour._meta.label_lower,
            disenrollment_model=DisenrollmentFour._meta.label_lower)

        self.visit_schedule_two.add_schedule(self.schedule_two_1)
        self.visit_schedule_two.add_schedule(self.schedule_two_2)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule_two)

    def test_enrolled_subject(self):
        enrolled_subject = EnrolledSubject()
        self.assertFalse(enrolled_subject.enrollments)

    def test_enrolled_subject_not_enrolled(self):
        subject_identifier = '111111'
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertFalse(enrolled_subject.enrollments)

    def test_get_enrollment_not_enrolled(self):
        """Asserts returns an empty list if not enrolled.
        """
        subject_identifier = '111111'
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertFalse(enrolled_subject.enrollments)

    def test_get_enrollment_enrolled(self):
        """Asserts returns an enrollment instance if enrolled.
        """
        subject_identifier = '111111'
        obj = EnrollmentTwo.objects.create(
            subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(enrolled_subject.enrollments, [obj])

    def test_get_enrollment_enrolled_many(self):
        """Asserts returns an empty list if not enrolled.
        """
        subject_identifier = '111111'
        obj1 = EnrollmentTwo.objects.create(
            subject_identifier=subject_identifier)
        obj2 = EnrollmentFour.objects.create(
            subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(enrolled_subject.enrollments, [obj1, obj2])

    def test_schedules(self):
        """Asserts returns one schedule if one enrollment.
        """
        subject_identifier = '111111'
        EnrollmentTwo.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(
            [s.name for s in enrolled_subject.schedules.values()],
            ['schedule_two'])

    def test_schedules_many(self):
        """Asserts returns two schedules if two enrollments.
        """
        subject_identifier = '111111'
        EnrollmentTwo.objects.create(subject_identifier=subject_identifier)
        EnrollmentFour.objects.create(
            subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(
            [s.name for s in enrolled_subject.schedules.values()],
            ['schedule_four', 'schedule_two'])

    def test_gets_correct_enrollments_if_many_others(self):
        subject_identifier = '111111'
        obj = EnrollmentTwo.objects.create(
            subject_identifier=subject_identifier)
        for i in range(0, 5):
            EnrollmentFour.objects.create(subject_identifier=str(i))
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(enrolled_subject.enrollments, [obj])

    def test_get_enrollment_enrolled5(self):
        """Asserts returns None for unknown schedule.
        """
        subject_identifier = '111111'
        EnrollmentTwo.objects.create(subject_identifier=subject_identifier)
        EnrollmentFour.objects.create(subject_identifier=subject_identifier)
        self.assertRaises(
            SiteVisitScheduleError,
            EnrolledSubject,
            subject_identifier=subject_identifier,
            visit_schedule_name='blah')

    def test_get_enrollment_enrolled6(self):
        """Asserts returns the correct instances for the schedule.
        """
        subject_identifier = '111111'
        EnrollmentTwo.objects.create(subject_identifier=subject_identifier)
        EnrollmentFour.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier,
            schedule_name='schedule_four')
        self.assertEqual(len(enrolled_subject.enrollments), 1)
