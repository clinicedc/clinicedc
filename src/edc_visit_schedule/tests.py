from django.test import TestCase

from edc_example.models import Enrollment, EnrollmentTwo, EnrollmentThree, Disenrollment, SubjectVisit, SubjectOffstudy

from .exceptions import AlreadyRegistered, ScheduleError, CrfError, VisitScheduleError
from .schedule import Schedule
from .site_visit_schedules import site_visit_schedules
from .visit import Crf
from .visit_schedule import VisitSchedule
from edc_example.factories import SubjectConsentFactory


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
        self.assertTrue(site_visit_schedules.get_visit_schedule('subject_visit_schedule'))

    def test_get_schedule_by_name(self):
        self.assertTrue(site_visit_schedules.get_schedule('schedule1'))
        schedule = site_visit_schedules.get_schedule('schedule1')
        self.assertEqual(schedule.name, 'schedule1')

    def test_get_schedule_by_enrollment_model_label(self):
        self.assertTrue(site_visit_schedules.get_schedule(Enrollment._meta.label_lower))
        schedule = site_visit_schedules.get_schedule(Enrollment._meta.label_lower)
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
        schedule = Schedule('schedule-one')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_schedule, schedule)

    def test_visit_already_added_to_schedule(self):
        schedule = Schedule('schedule-one')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000')
        self.assertRaises(AlreadyRegistered, schedule.add_visit, '1000')

    def test_schedule_detects_duplicate_timepoint(self):
        schedule = Schedule('schedule-one')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=1)

    def test_schedule_detects_duplicate_base_interval(self):
        schedule = Schedule('schedule-one')
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1, base_interval=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=2, base_interval=1)

    def test_add_schedule_detects_null_enrollment(self):
        schedule = Schedule('schedule-one')
        self.assertRaises(VisitScheduleError, self.visit_schedule.add_schedule, schedule)

    def test_gets_ordered_visits(self):
        """Assert visits are ordered by timepoint default."""
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals([x.timepoint for x in schedule.visits], [1, 2, 3, 5, 7])

    def test_gets_previous_visit(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('5000'), schedule.get_visit('3000'))

    def test_gets_previous_visit2(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('1000'), None)

    def test_gets_next_visit(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('5000', 1), schedule.get_visit('7000'))

    def test_gets_visit_forwards(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('3000', 1), schedule.get_visit('5000'))

    def test_gets_visit_forwards2(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 3), schedule.get_visit('5000'))

    def test_gets_visit_forwards3(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 10), None)

    def test_gets_visit_backwards(self):
        schedule = Schedule('schedule-one')
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('7000', -3), schedule.get_visit('2000'))

    def test_crfs_unique_show_order(self):
        crfs = (
            Crf(show_order=10, model='edc_example.CrfOne'),
            Crf(show_order=20, model='edc_example.CrfTwo'),
            Crf(show_order=20, model='edc_example.CrfThree'),
        )
        schedule = Schedule('schedule-one')
        self.assertRaises(CrfError, schedule.add_visit, '1000', timepoint=0, crfs=crfs)

    def test_enrollment_model_knows_schedule_name(self):
        """Assert if schedule name provided on meta, does not need to be provided explicitly."""
        SubjectConsentFactory(subject_identifier='111111')
        # schedule name not provided and is not on Meta
        self.assertRaises(AttributeError, Enrollment.objects.create, subject_identifier='111111', is_eligible=True)
        # schedule name not provided and is on Meta
        try:
            EnrollmentThree.objects.create(subject_identifier='111111', is_eligible=True)
        except AttributeError:
            self.fail('AttributeError unexpectedly raised')
