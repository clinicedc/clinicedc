from django.test import TestCase

from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Crf
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_schedule.exceptions import AlreadyRegistered, ScheduleError, CrfError

from edc_example.models import SubjectConsent, SubjectVisit
from edc_visit_schedule.schedule import Schedule


bad_visit_schedule = VisitSchedule(
    name='Bad Visit Schedule',
    app_label='edc_example',
)


class TestVisitSchedule(TestCase):

    def setUp(self):
        self.bad_visit_schedule = VisitSchedule(
            name='Bad Visit Schedule',
            app_label='edc_example',
            visit_model=SubjectVisit,
        )

    def test_get_visit_schedule_by_name(self):
        self.assertTrue(site_visit_schedules.get_visit_schedule('subject_visit_schedule'))

    def test_get_schedule_by_name(self):
        self.assertTrue(site_visit_schedules.get_schedule('schedule-1'))
        schedule = site_visit_schedules.get_schedule('schedule-1')
        self.assertEqual(schedule.name, 'schedule-1')

    def test_get_schedule_by_enrollment_model_label(self):
        self.assertTrue(site_visit_schedules.get_schedule(SubjectConsent._meta.label_lower))
        schedule = site_visit_schedules.get_schedule(SubjectConsent._meta.label_lower)
        self.assertEqual(schedule.enrollment_model, SubjectConsent)

    def test_get_schedule_by_enrollment_model(self):
        self.assertTrue(site_visit_schedules.get_schedule(SubjectConsent))
        schedule = site_visit_schedules.get_schedule(SubjectConsent)
        self.assertEqual(schedule.enrollment_model, SubjectConsent)

    def test_schedule_get_visits(self):
        visit_schedule = site_visit_schedules.get_visit_schedule('subject_visit_schedule')
        for schedule in visit_schedule.schedules.values():
            self.assertIsInstance(schedule.visits, list)

    def test_schedule_already_registered(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_schedule, schedule)

    def test_visit_already_added_to_schedule(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000')
        self.assertRaises(AlreadyRegistered, schedule.add_visit, '1000')

    def test_schedule_detects_duplicate_timepoint(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=1)

    def test_schedule_detects_duplicate_base_interval(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        schedule = self.bad_visit_schedule.add_schedule(schedule)
        schedule.add_visit('1000', timepoint=1, base_interval=1)
        self.assertRaises(ScheduleError, schedule.add_visit, '2000', timepoint=2, base_interval=1)

    def test_gets_ordered_visits(self):
        """Assert visits are ordered by timepoint default."""
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals([x.timepoint for x in schedule.visits], [1, 2, 3, 5, 7])

    def test_gets_previous_visit(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('5000'), schedule.get_visit('3000'))

    def test_gets_previous_visit2(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_previous_visit('1000'), None)

    def test_gets_next_visit(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('5000', 1), schedule.get_visit('7000'))

    def test_gets_visit_forwards(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('3000', 1), schedule.get_visit('5000'))

    def test_gets_visit_forwards2(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 3), schedule.get_visit('5000'))

    def test_gets_visit_forwards3(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('1000', 10), None)

    def test_gets_visit_backwards(self):
        schedule = Schedule('schedule-one', enrollment_model=SubjectConsent)
        for i in [1, 5, 3, 7, 2]:
            schedule.add_visit('{}000'.format(i), timepoint=i, base_interval=i)
        self.assertEquals(schedule.get_visit('7000', -3), schedule.get_visit('2000'))

    def test_crfs_unique_show_order(self):
        crfs = (
            Crf(show_order=10, app_label='edc_example', model_name='CrfOne'),
            Crf(show_order=20, app_label='edc_example', model_name='CrfTwo'),
            Crf(show_order=20, app_label='edc_example', model_name='CrfThree'),
        )
        schedule = Schedule('schedule', enrollment_model=SubjectConsent)
        self.assertRaises(CrfError, schedule.add_visit, '1000', timepoint=0, crfs=crfs)
