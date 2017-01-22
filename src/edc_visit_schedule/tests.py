from dateutil.relativedelta import relativedelta
from django.test import TestCase

from edc_base.utils import get_utcnow
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory
from edc_example.models import (
    Enrollment, EnrollmentTwo, EnrollmentThree, Disenrollment, SubjectVisit, SubjectOffstudy,
    Appointment, DisenrollmentThree)

from .exceptions import EnrollmentError, AlreadyRegistered, ScheduleError, CrfError, VisitScheduleError
from .schedule import Schedule
from .site_visit_schedules import site_visit_schedules
from .visit import Crf
from .visit_schedule import VisitSchedule


class TestVisitSchedule(TestCase):

    def setUp(self):
        self.bad_visit_schedule = VisitSchedule(
            name='subject_visit_schedule',
            verbose_name='Bad Visit Schedule',
            app_label='edc_example',
            visit_model=SubjectVisit._meta.label_lower,
            default_enrollment_model=Enrollment._meta.label_lower,
            default_disenrollment_model=Disenrollment._meta.label_lower,
            offstudy_model=SubjectOffstudy._meta.label_lower,
        )

        self.visit_schedule = VisitSchedule(
            name='subject_visit_schedule',
            verbose_name='Bad Visit Schedule',
            app_label='edc_example',
            visit_model=SubjectVisit._meta.label_lower,
            offstudy_model=SubjectOffstudy._meta.label_lower,
        )

    def test_load_incomplete_visit_schedule(self):
        self.assertRaises(
            VisitScheduleError, VisitSchedule,
            name='subject_visit_schedule',
            verbose_name='Bad Visit Schedule',
            app_label='edc_example',
        )

    def test_get_visit_schedule_by_name(self):
        self.assertTrue(
            site_visit_schedules.get_visit_schedule(
                'subject_visit_schedule'))

    def test_get_schedule_by_name(self):
        self.assertTrue(site_visit_schedules.get_schedule('schedule1'))
        schedule = site_visit_schedules.get_schedule('schedule1')
        self.assertEqual(schedule.name, 'schedule1')

    def test_get_schedule_by_enrollment_model_label(self):
        self.assertTrue(
            site_visit_schedules.get_schedule(Enrollment._meta.label_lower))
        schedule = site_visit_schedules.get_schedule(
            Enrollment._meta.label_lower)
        self.assertEqual(schedule.enrollment_model, Enrollment)

    def test_get_schedule_by_enrollmenttwo_model_label(self):
        self.assertTrue(site_visit_schedules.get_schedule(EnrollmentTwo._meta.label_lower))
        schedule = site_visit_schedules.get_schedule(EnrollmentTwo._meta.label_lower)
        self.assertEqual(schedule.enrollment_model, EnrollmentTwo)

    def test_get_schedule_by_enrollment_model(self):
        self.assertTrue(site_visit_schedules.get_schedule(Enrollment))
        schedule = site_visit_schedules.get_schedule(Enrollment)
        self.assertEqual(schedule.enrollment_model, Enrollment)

    def test_get_schedule_by_enrollmenttwo_model(self):
        self.assertTrue(site_visit_schedules.get_schedule(EnrollmentTwo))
        schedule = site_visit_schedules.get_schedule(EnrollmentTwo)
        self.assertEqual(schedule.enrollment_model, EnrollmentTwo)

    def test_schedule_get_visits(self):
        visit_schedule = site_visit_schedules.get_visit_schedule('subject_visit_schedule')
        for schedule in visit_schedule.schedules.values():
            self.assertIsInstance(schedule.visits, list)

    def test_schedule_already_registered(self):
        schedule = Schedule('schedule1')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_schedule, schedule)

    def test_visit_already_added_to_schedule(self):
        schedule = Schedule('schedule1')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000')
        self.assertRaises(AlreadyRegistered, schedule.add_visit, '1000')

    def test_schedule_detects_duplicate_timepoint(self):
        schedule = Schedule('schedule1')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=1)

    def test_schedule_detects_duplicate_base_interval(self):
        schedule = Schedule('schedule1')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1, base_interval=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=2, base_interval=1)

    def test_add_schedule_detects_null_enrollment(self):
        schedule = Schedule('schedule1')
        self.assertRaises(VisitScheduleError, self.visit_schedule.add_schedule, schedule)

    def test_gets_ordered_visits(self):
        """Assert visits are ordered by timepoint default."""
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals([x.timepoint for x in schedule.visits], [1, 2, 3, 5, 7])

    def test_gets_previous_visit(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('5000'), schedule.get_visit('3000'))

    def test_gets_previous_visit2(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('1000'), None)

    def test_gets_next_visit(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('5000', 1), schedule.get_visit('7000'))

    def test_gets_visit_forwards(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('3000', 1), schedule.get_visit('5000'))

    def test_gets_visit_forwards2(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 3), schedule.get_visit('5000'))

    def test_gets_visit_forwards3(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 10), None)

    def test_gets_visit_backwards(self):
        schedule = Schedule('schedule1')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('7000', -3), schedule.get_visit('2000'))

    def test_crfs_unique_show_order(self):
        crfs = (
            Crf(show_order=10, model='edc_example.CrfOne'),
            Crf(show_order=20, model='edc_example.CrfTwo'),
            Crf(show_order=20, model='edc_example.CrfThree'),
        )
        schedule = Schedule('schedule1')
        self.assertRaises(CrfError, schedule.add_visit, '1000', timepoint=0, crfs=crfs)

    def test_enrollment_model_knows_schedule_name(self):
        """Assert if schedule name provided on meta, does not need to be provided explicitly."""
        SubjectConsentFactory(subject_identifier='111111')
        # schedule name not provided and is not on Meta
        try:
            Enrollment.objects.create(subject_identifier='111111', is_eligible=True)
        except (AttributeError, ScheduleError):
            self.fail('Error unexpectedly raised')
        # schedule name not provided and is on Meta
        try:
            EnrollmentThree.objects.create(subject_identifier='111111', is_eligible=True)
        except (AttributeError, ScheduleError):
            self.fail('Error unexpectedly raised')

    def test_get_schedule_names(self):
        """Assert site can return list of schedule names.

        This will break of edc-example visit_schedules.py changes."""
        self.assertEqual(
            site_visit_schedules.get_schedule_names('subject_visit_schedule'),
            ['subject_visit_schedule.schedule1', 'subject_visit_schedule.schedule2',
             'subject_visit_schedule.schedule3'])

    def test_get_visit_schedule_names(self):
        """Assert site can return list of visit schedule names.

        This will break of edc-example visit_schedules.py changes."""
        self.assertEqual(
            site_visit_schedules.get_visit_schedule_names(),
            ['subject_visit_schedule', 'subject_visit_schedule2'])

    def test_get_enrollment_for_subject_from_site(self):
        """Asserts site can return the enrollment instance."""
        SubjectConsentFactory(
            subject_identifier='111111',
            consent_datetime=get_utcnow() - relativedelta(weeks=4),
            identity='111111',
            confirm_identity='111111')
        enrollment_datetime = get_utcnow()
        Enrollment.objects.create(subject_identifier='111111', report_datetime=enrollment_datetime)
        visit_schedule_name, schedule_name = Enrollment._meta.visit_schedule_name.split('.')
        self.assertEqual(
            enrollment_datetime,
            site_visit_schedules.enrollment(
                '111111', visit_schedule_name, schedule_name).report_datetime)
        EnrollmentTwo.objects.create(subject_identifier='111111', report_datetime=enrollment_datetime)
        visit_schedule_name, schedule_name = EnrollmentTwo._meta.visit_schedule_name.split('.')
        self.assertEqual(
            enrollment_datetime,
            site_visit_schedules.enrollment(
                '111111', visit_schedule_name, schedule_name).report_datetime)
        EnrollmentThree.objects.create(subject_identifier='111111', report_datetime=enrollment_datetime)
        visit_schedule_name, schedule_name = EnrollmentThree._meta.visit_schedule_name.split('.')
        self.assertEqual(
            enrollment_datetime,
            site_visit_schedules.enrollment(
                '111111', visit_schedule_name, schedule_name).report_datetime)

    def test_no_disenrollment_without_enrollment(self):
        SubjectConsentFactory(
            subject_identifier='111111',
            consent_datetime=get_utcnow() - relativedelta(weeks=4),
            identity='111111',
            confirm_identity='111111')
        self.assertRaises(EnrollmentError, Disenrollment.objects.create, subject_identifier='111111')

    def test_get_enrollment_from_disenrollment(self):
        """Asserts site can return the enrollment instance."""
        SubjectConsentFactory(
            subject_identifier='111111',
            consent_datetime=get_utcnow() - relativedelta(weeks=4),
            identity='111111',
            confirm_identity='111111')
        enrollment_datetime = get_utcnow()
        enrollment = EnrollmentThree.objects.create(subject_identifier='111111', report_datetime=enrollment_datetime)
        disenrollment = DisenrollmentThree.objects.create(subject_identifier='111111', schedule_name='schedule3')
        self.assertEqual(disenrollment.enrollment, enrollment)

    def test_blocks_enrollment_not_for_schedule(self):
        """Asserts that <enrollment>.<schedule_name> matches configuration in schedule."""
        for i in range(1, 4):
            SubjectConsentFactory(
                subject_identifier='111111' + str(i),
                consent_datetime=get_utcnow() - relativedelta(weeks=4),
                identity='111111' + str(i),
                confirm_identity='111111' + str(i),)
        try:
            EnrollmentTwo.objects.create(subject_identifier='1111111', schedule_name='schedule2')
        except ScheduleError:
            self.fail('Unexpectedly raised ScheduleError')
        self.assertRaises(
            ScheduleError, Enrollment.objects.create, subject_identifier='1111113', schedule_name='schedule3')
        self.assertRaises(
            ScheduleError, EnrollmentThree.objects.create, subject_identifier='1111112', schedule_name='schedule1')

    def test_get_last_visit(self):
        for i in range(1, 4):
            SubjectConsentFactory(
                subject_identifier='111111' + str(i),
                consent_datetime=get_utcnow() - relativedelta(weeks=4),
                identity='111111' + str(i),
                confirm_identity='111111' + str(i),)
        Enrollment.objects.create(subject_identifier='1111111')
        Enrollment.objects.create(subject_identifier='1111112')
        Enrollment.objects.create(subject_identifier='1111113')
        EnrollmentTwo.objects.create(subject_identifier='1111111')
        EnrollmentTwo.objects.create(subject_identifier='1111112')
        EnrollmentTwo.objects.create(subject_identifier='1111113')
        EnrollmentThree.objects.create(subject_identifier='1111111')
        EnrollmentThree.objects.create(subject_identifier='1111112')
        EnrollmentThree.objects.create(subject_identifier='1111113')
        for appointment in Appointment.objects.all().order_by('subject_identifier', 'appt_datetime'):
            SubjectVisitFactory(appointment=appointment, report_datetime=appointment.appt_datetime)
        self.assertEqual(
            SubjectVisit.objects.filter(
                subject_identifier='1111113').order_by('report_datetime').last().report_datetime,
            site_visit_schedules.last_visit_datetime('1111113'))
        self.assertEqual(
            SubjectVisit.objects.filter(
                subject_identifier='1111112').order_by('report_datetime').last().report_datetime,
            site_visit_schedules.last_visit_datetime('1111112'))
        self.assertEqual(
            SubjectVisit.objects.filter(
                subject_identifier='1111111').order_by('report_datetime').last().report_datetime,
            site_visit_schedules.last_visit_datetime('1111111'))
