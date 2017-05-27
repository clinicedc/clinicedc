from django.test import TestCase, tag

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..visit_schedule import VisitSchedule
from .models import SubjectVisit, SubjectOffstudy, DeathReport
from .models import Enrollment, Disenrollment, DisenrollmentTwo, EnrollmentTwo
from edc_visit_schedule.site_visit_schedules import SiteVisitScheduleError
from edc_base.utils import get_utcnow
from edc_visit_schedule.visit_schedule.visit_schedule import VisitScheduleModelError
from edc_visit_schedule.model_mixins import EnrollmentModelError


@tag('site')
class TestSiteVisitSchedule(TestCase):

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

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport,
            enrollment_model=EnrollmentTwo,
            disenrollment_model=DisenrollmentTwo)

        self.schedule_two = Schedule(
            name='schedule_two',
            enrollment_model=EnrollmentTwo._meta.label_lower,
            disenrollment_model=DisenrollmentTwo._meta.label_lower)

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule_two.add_schedule(self.schedule_two)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)
        site_visit_schedules.register(self.visit_schedule_two)

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

    def test_get_schedule_by_name(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(schedule_name=self.schedule.name))
        self.assertEqual(
            self.schedule,
            site_visit_schedules.get_schedule(schedule_name=self.schedule.name))

    def test_get_schedule_by_enrollment_model_label(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model=Enrollment._meta.label_lower))
        schedule = site_visit_schedules.get_schedule(
            model=Enrollment._meta.label_lower)
        self.assertEqual(schedule.enrollment_model, Enrollment)

    def test_get_schedule_by_enrollment_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model=Enrollment))
        schedule = site_visit_schedules.get_schedule(model=Enrollment)
        self.assertEqual(schedule.enrollment_model, Enrollment)

    def test_get_schedule_by_enrollmenttwo_model_label(self):

        # in two steps
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=EnrollmentTwo._meta.visit_schedule_name.split('.')[0])
        self.assertEqual(visit_schedule.models.enrollment_model, EnrollmentTwo)

        schedule = visit_schedule.get_schedule(model=EnrollmentTwo)
        self.assertEqual(schedule.enrollment_model, EnrollmentTwo)

        # in one step
        schedule = site_visit_schedules.get_schedule(
            model=EnrollmentTwo._meta.label_lower)
        self.assertEqual(schedule.enrollment_model, EnrollmentTwo)

    def test_get_schedule_by_enrollmenttwo_model(self):
        self.assertIsNotNone(
            site_visit_schedules.get_schedule(model=EnrollmentTwo))
        schedule = site_visit_schedules.get_schedule(model=EnrollmentTwo)
        self.assertEqual(schedule.enrollment_model, EnrollmentTwo)

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

    def test_get_enrollment_for_subject_from_site(self):
        """Asserts site can return the enrollment instance.
        """
        enrollment_datetime = get_utcnow()
        for model in [Enrollment, EnrollmentTwo]:
            model.objects.create(
                subject_identifier='111111', report_datetime=enrollment_datetime)
            visit_schedule_name, schedule_name = (
                Enrollment._meta.visit_schedule_name.split('.'))
            self.assertEqual(
                enrollment_datetime,
                site_visit_schedules.enrollment(
                    '111111', visit_schedule_name, schedule_name).report_datetime)

    def test_get_enrollment_from_schedule(self):

        schedule = site_visit_schedules.get_schedule(schedule_name='schedule')
        self.assertRaises(
            schedule.enrollment_model.DoesNotExist,
            schedule.enrollment(subject_identifier='1'))

        obj = Enrollment.objects.create(subject_identifier='1')
        schedule = site_visit_schedules.get_schedule(schedule_name='schedule')
        self.assertEqual(obj, schedule.enrollment(subject_identifier='1'))

    @tag('models')
    def test_enrollment(self):
        obj = Enrollment.objects.create()
        self.assertEqual(obj.visit_schedule_name, 'visit_schedule')
        self.assertEqual(obj.schedule_name, 'schedule')
        self.assertIsNotNone(obj.visit_schedule)
        self.assertIsNotNone(obj.schedule)

    @tag('models')
    def test_enrollment_cannot_change(self):
        obj = Enrollment.objects.create()
        obj.visit_schedule_name = 'blah'
        obj.schedule_name = 'blah'
        self.assertRaises(EnrollmentModelError, obj.save)
