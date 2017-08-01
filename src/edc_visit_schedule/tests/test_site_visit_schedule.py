from django.test import TestCase, tag

from ..model_mixins import EnrollmentModelError
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..site_visit_schedules import AlreadyRegisteredVisitSchedule
from ..visit_schedule import VisitSchedule
from .models import Enrollment, EnrollmentTwo, EnrollmentThree, EnrollmentFour
from .models import DisenrollmentThree, DisenrollmentFour


@tag('site')
class TestSiteVisitSchedule(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')

    def test_register_no_schedules(self):
        site_visit_schedules._registry = {}
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.register, self.visit_schedule)

    def test_already_registered(self):
        site_visit_schedules._registry = {}
        schedule = Schedule(
            name='schedule',
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')
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
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')

        self.schedule = Schedule(
            name='schedule',
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            disenrollment_model='edc_visit_schedule.disenrollmenttwo')

        self.schedule_two = Schedule(
            name='schedule_two',
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            disenrollment_model='edc_visit_schedule.disenrollmenttwo')

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

    def test_get_schedule_by_enrollment_model_label(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.enrollment'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.enrollment')
        self.assertEqual(schedule.enrollment_model_cls, Enrollment)

    def test_get_schedule_by_enrollment_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.enrollment'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.enrollment')
        self.assertEqual(schedule.enrollment_model_cls, Enrollment)

    def test_get_schedule_by_enrollmenttwo_model_label(self):

        # in two steps
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=EnrollmentTwo._meta.visit_schedule_name.split('.')[0])
        self.assertEqual(
            visit_schedule.models.enrollment_model, EnrollmentTwo._meta.label_lower)

        schedule = visit_schedule.get_schedule(
            model=EnrollmentTwo._meta.label_lower)
        self.assertEqual(schedule.enrollment_model_cls, EnrollmentTwo)

        # in one step
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.enrollmenttwo')
        self.assertEqual(schedule.enrollment_model_cls, EnrollmentTwo)

    def test_get_schedule_by_enrollmenttwo_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model='edc_visit_schedule.enrollmenttwo'))
        schedule = site_visit_schedules.get_schedule(
            model='edc_visit_schedule.enrollmenttwo')
        self.assertEqual(schedule.enrollment_model_cls, EnrollmentTwo)

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

    def test_enrollment(self):
        obj = Enrollment.objects.create()
        self.assertEqual(obj.visit_schedule_name, 'visit_schedule')
        self.assertEqual(obj.schedule_name, 'schedule')
        self.assertIsNotNone(obj.visit_schedule)
        self.assertIsNotNone(obj.schedule)

    def test_enrollment_cannot_change_visit_schedule(self):
        obj = Enrollment.objects.create()
        obj.visit_schedule_name = 'blah'
        obj.schedule_name = 'blah'
        self.assertRaises(EnrollmentModelError, obj.save)

    def test_enrollment_cannot_change_schedule(self):
        obj = Enrollment.objects.create()
        obj.schedule_name = 'blah'
        self.assertRaises(EnrollmentModelError, obj.save)


@tag('site')
class TestSiteVisitSchedule2(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')

        self.visit_schedule2 = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            enrollment_model='edc_visit_schedule.enrollmenttwwo',
            disenrollment_model='edc_visit_schedule.disenrollmenttwo')

        self.schedule = Schedule(
            name='schedule',
            enrollment_model='edc_visit_schedule.enrollment',
            disenrollment_model='edc_visit_schedule.disenrollment')

        self.schedule2 = Schedule(
            name='schedule_two',
            enrollment_model='edc_visit_schedule.enrollmenttwo',
            disenrollment_model='edc_visit_schedule.disenrollmenttwo')

        self.schedule3 = Schedule(
            name='schedule_three',
            enrollment_model=EnrollmentThree._meta.label_lower,
            disenrollment_model=DisenrollmentThree._meta.label_lower)

        self.schedule4 = Schedule(
            name='schedule_four',
            enrollment_model=EnrollmentFour._meta.label_lower,
            disenrollment_model=DisenrollmentFour._meta.label_lower)

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
