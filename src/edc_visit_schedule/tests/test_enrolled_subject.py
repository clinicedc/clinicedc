from django.test import TestCase, tag

from ..enrolled_subject import EnrolledSubject
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..visit_schedule import VisitSchedule
from .models import SubjectVisit, SubjectOffstudy, DeathReport, Disenrollment
from .models import Enrollment, EnrollmentTwo, EnrollmentThree
from edc_visit_schedule.site_visit_schedules import SiteVisitScheduleError


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
            disenrollment_model=Disenrollment._meta.label_lower)

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

    def test_get_enrollment_not_enrolled(self):
        """Asserts returns an empty list if not enrolled.
        """
        subject_identifier = '111111'
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(len(enrolled_subject.enrollments()), 0)

    def test_get_enrollment_enrolled(self):
        """Asserts returns the enrollment instance.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(len(enrolled_subject.enrollments()), 1)

    def test_get_enrollment_enrolled2(self):
        """Asserts returns the enrollment instance even if others
        exist.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        for i in range(0, 5):
            Enrollment.objects.create(subject_identifier=str(i))
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(len(enrolled_subject.enrollments()), 1)

    def test_get_enrollment_enrolled3(self):
        """Asserts returns all enrollment instances if more than one exists.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        EnrollmentThree.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(len(enrolled_subject.enrollments()), 2)

    def test_get_enrollment_enrolled4(self):
        """Asserts returns all instances for the visit schedule.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        EnrollmentThree.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier,
            visit_schedule_name='visit_schedule')
        self.assertEqual(len(enrolled_subject.enrollments()), 2)

    def test_get_enrollment_enrolled5(self):
        """Asserts returns None for unknown schedule.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        EnrollmentThree.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertRaises(
            SiteVisitScheduleError,
            enrolled_subject.enrollments, visit_schedule_name='blah')

    @tag('1')
    def test_get_enrollment_enrolled6(self):
        """Asserts returns the correct instances for the schedule.
        """
        subject_identifier = '111111'
        Enrollment.objects.create(subject_identifier=subject_identifier)
        EnrollmentThree.objects.create(subject_identifier=subject_identifier)
        enrolled_subject = EnrolledSubject(
            subject_identifier=subject_identifier)
        self.assertEqual(len(enrolled_subject.enrollments(
            schedule_name='schedule_three')), 1)

#         enrollment_datetime = get_utcnow()
#         enrollment = Enrollment.objects.create(
#             subject_identifier='111111', report_datetime=enrollment_datetime)
#         disenrollment = Disenrollment.objects.create(
#             subject_identifier='111111')
#         self.assertEqual(disenrollment.enrollment, enrollment)
#
#     def test_get_disenrollment(self):
#         """Asserts site can return the enrollment instance.
#         """
#         enrollment_datetime = get_utcnow()
#         enrollment = Enrollment.objects.create(
#             subject_identifier='111111', report_datetime=enrollment_datetime)
#         disenrollment = Disenrollment.objects.create(
#             subject_identifier='111111')
#         self.assertEqual(disenrollment.enrollment, enrollment)
