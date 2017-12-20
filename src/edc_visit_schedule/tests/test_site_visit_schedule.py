from django.test import TestCase, tag
from uuid import uuid4

from ..model_mixins import OnScheduleModelError
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..site_visit_schedules import AlreadyRegisteredVisitSchedule
from ..visit_schedule import VisitSchedule
from .models import OnSchedule, OnScheduleTwo, OnScheduleThree, OnScheduleFour
from .models import OffScheduleThree, OffScheduleFour


class TestSiteVisitSchedule(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

    def test_register_no_schedules(self):
        site_visit_schedules._registry = {}
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.register, self.visit_schedule)

    def test_already_registered(self):
        site_visit_schedules._registry = {}
        schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')
        self.visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(self.visit_schedule)
        self.assertRaises(
            AlreadyRegisteredVisitSchedule,
            site_visit_schedules.register, self.visit_schedule)


@tag('site')
class TestSiteVisitSchedule1(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onscheduletwo',
            offschedule_model='edc_visit_schedule.offscheduletwo')

        self.schedule_two = Schedule(
            name='schedule_two',
            onschedule_model='edc_visit_schedule.onscheduletwo',
            offschedule_model='edc_visit_schedule.offscheduletwo')

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule_two.add_schedule(self.schedule_two)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)
        site_visit_schedules.register(self.visit_schedule_two)

    def test_visit_schedules(self):
        self.assertIn(
            self.visit_schedule,
            site_visit_schedules.visit_schedules.values())
        self.assertIn(
            self.visit_schedule_two,
            site_visit_schedules.visit_schedules.values())

    def test_get_visit_schedules(self):
        """Asserts returns a dictionary of visit schedules.
        """
        self.assertEqual(
            len(site_visit_schedules.get_visit_schedules()), 2)

    def test_get_visit_schedule_by_name(self):
        visit_schedule_name = self.visit_schedule.name
        self.assertEqual(
            self.visit_schedule,
            site_visit_schedules.get_visit_schedule(visit_schedule_name=visit_schedule_name))

    def test_get_visit_schedule_by_name_raises(self):
        visit_schedule_name = 'blahblah'
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name=visit_schedule_name)

    def test_get_visit_schedule_by_name_raises2(self):
        visit_schedule_name = 'blah.'
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name=visit_schedule_name)

    def test_get_visit_schedule_by_name_raises3(self):
        visit_schedule_name = '.blah'
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name=visit_schedule_name)

    def test_get_schedule_by_name(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(schedule_name=self.schedule.name))
        self.assertEqual(
            self.schedule,
            site_visit_schedules.get_schedule(schedule_name=self.schedule.name))

    def test_get_schedule_by_badname(self):
        self.assertIsNone(
            site_visit_schedules.get_schedule(schedule_name='blah'))

    def test_get_schedule_by_meta(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(
                visit_schedule_name='visit_schedule.schedule'))
        self.assertEqual(
            self.schedule,
            site_visit_schedules.get_schedule(
                visit_schedule_name='visit_schedule.schedule'))

    def test_get_schedule_by_bad_model(self):
        self.assertIsNone(site_visit_schedules.get_schedule(model='blah'))

    def test_get_schedule_by_onschedule_model_label(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.onschedule'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.onschedule')
        self.assertEqual(schedule.onschedule_model_cls, OnSchedule)

    def test_get_schedule_by_onschedule_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.onschedule'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.onschedule')
        self.assertEqual(schedule.onschedule_model_cls, OnSchedule)

    def test_get_schedule_by_onscheduletwo_model_label(self):

        # in two steps
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=OnScheduleTwo._meta.visit_schedule_name.split('.')[0])
        self.assertEqual(
            visit_schedule.models.onschedule_model, OnScheduleTwo._meta.label_lower)

        schedule = visit_schedule.get_schedule(
            model=OnScheduleTwo._meta.label_lower)
        self.assertEqual(schedule.onschedule_model_cls, OnScheduleTwo)

        # in one step
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.onscheduletwo')
        self.assertEqual(schedule.onschedule_model_cls, OnScheduleTwo)

    def test_get_schedule_by_onscheduletwo_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.onscheduletwo'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.onscheduletwo')
        self.assertEqual(schedule.onschedule_model_cls, OnScheduleTwo)

    def test_get_schedules(self):
        """Assert site can return list of schedules.
        """
        self.assertEqual(
            len(site_visit_schedules.get_schedules(visit_schedule_name='visit_schedule')), 1)
        self.assertEqual(
            len(site_visit_schedules.get_schedules(visit_schedule_name='visit_schedule_two')), 1)

    def test_get_schedule_names(self):
        """Assert site can return list of schedule names.
        """
        self.assertEqual(
            site_visit_schedules.get_schedule_names('visit_schedule'),
            ['visit_schedule.schedule'])
        self.assertEqual(
            site_visit_schedules.get_schedule_names('visit_schedule_two'),
            ['visit_schedule_two.schedule_two'])

    def test_get_visit_schedule_names(self):
        """Assert site can return list of visit schedule names.
        """
        self.assertEqual(
            site_visit_schedules.get_visit_schedule_names(),
            ['visit_schedule', 'visit_schedule_two'])

    def test_onschedule(self):
        obj = OnSchedule.objects.create(
            consent_identifier=uuid4())
        self.assertEqual(obj.visit_schedule_name, 'visit_schedule')
        self.assertEqual(obj.schedule_name, 'schedule')
        self.assertIsNotNone(obj.visit_schedule)
        self.assertIsNotNone(obj.schedule)


class TestSiteVisitSchedule2(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

        self.visit_schedule2 = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onscheduletwwo',
            offschedule_model='edc_visit_schedule.offscheduletwo')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

        self.schedule2 = Schedule(
            name='schedule_two',
            onschedule_model='edc_visit_schedule.onscheduletwo',
            offschedule_model='edc_visit_schedule.offscheduletwo')

        self.schedule3 = Schedule(
            name='schedule_three',
            onschedule_model=OnScheduleThree._meta.label_lower,
            offschedule_model=OffScheduleThree._meta.label_lower)

        self.schedule4 = Schedule(
            name='schedule_four',
            onschedule_model=OnScheduleFour._meta.label_lower,
            offschedule_model=OffScheduleFour._meta.label_lower)

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)

        self.visit_schedule2.add_schedule(self.schedule2)
        self.visit_schedule2.add_schedule(self.schedule4)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)
        site_visit_schedules.register(self.visit_schedule2)

    def test_get_schedules(self):
        """Assert site can return list of schedules.
        """
        self.assertEqual(
            len(site_visit_schedules.get_schedules('visit_schedule')), 2)
        self.assertEqual(
            len(site_visit_schedules.get_schedules('visit_schedule_two')), 2)

    def test_get_schedules_raises(self):
        """Assert site can return list of schedules.
        """
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_schedules, 'blah')

    def test_get_schedule_names(self):
        """Assert site can return list of schedule names.
        """
        self.assertEqual(
            site_visit_schedules.get_schedule_names('visit_schedule'),
            ['visit_schedule.schedule', 'visit_schedule.schedule_three'])

        self.assertEqual(
            site_visit_schedules.get_schedule_names('visit_schedule_two'),
            ['visit_schedule_two.schedule_four', 'visit_schedule_two.schedule_two'])
