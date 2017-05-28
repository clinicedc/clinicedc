from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from ..model_mixins import DisenrollmentError, EnrollmentModelError
from ..validator import ValidatorMetaValueError
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..visit import Crf, FormsCollectionError
from ..visit_schedule import VisitSchedule, VisitScheduleError, VisitScheduleModelError
from ..visit_schedule import VisitScheduleNameError, AlreadyRegisteredSchedule
from .models import Enrollment, EnrollmentThree, EnrollmentTwo
from .models import Disenrollment, DisenrollmentThree, DisenrollmentTwo
from .models import SubjectVisit, SubjectOffstudy, DeathReport
from collections import OrderedDict


@tag('visit')
class TestVisitSchedule(TestCase):

    def test_visit_schedule_name(self):
        """Asserts raises on invalid name.
        """
        self.assertRaises(
            VisitScheduleNameError,
            VisitSchedule,
            name='visit &&&& schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport,
            enrollment_model=Enrollment,
            disenrollment_model=Disenrollment)

    def test_visit_schedule_repr(self):
        """Asserts repr evaluates correctly.
        """
        v = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport,
            enrollment_model=Enrollment,
            disenrollment_model=Disenrollment)
        self.assertTrue(v.__repr__())

    def test_visit_schedule1(self):
        """Asserts can instantiate with model classes.
        """
        try:
            VisitSchedule(
                name='visit_schedule',
                verbose_name='Visit Schedule',
                visit_model=SubjectVisit,
                offstudy_model=SubjectOffstudy,
                death_report_model=DeathReport,
                enrollment_model=Enrollment,
                disenrollment_model=Disenrollment)
        except VisitScheduleError as e:
            self.fail(f'VisitScheduleError unepectedly raised {e}')

    def test_visit_schedule2(self):
        """Asserts can instantiate with model label_lower
        instead of model classes.
        """
        try:
            VisitSchedule(
                name='visit_schedule',
                verbose_name='Visit Schedule',
                visit_model=SubjectVisit._meta.label_lower,
                offstudy_model=SubjectOffstudy._meta.label_lower,
                death_report_model=DeathReport._meta.label_lower,
                enrollment_model=Enrollment._meta.label_lower,
                disenrollment_model=Disenrollment._meta.label_lower)
        except VisitScheduleError as e:
            self.fail(f'VisitScheduleError unepectedly raised {e}')

    def test_visit_schedule3(self):
        """Asserts raises on bad enrollment.
        """
        self.assertRaises(
            VisitScheduleModelError,
            VisitSchedule,
            name='visit_schedule',
            verbose_name='Visit Schedule',
            visit_model=SubjectVisit._meta.label_lower,
            offstudy_model=SubjectOffstudy._meta.label_lower,
            death_report_model=DeathReport._meta.label_lower,
            enrollment_model='blah.blah',
            disenrollment_model=Disenrollment._meta.label_lower)

    def test_visit_schedule4(self):
        """Asserts raises on bad disenrollment.
        """
        self.assertRaises(
            VisitScheduleModelError,
            VisitSchedule,
            name='visit_schedule',
            verbose_name='Visit Schedule',
            visit_model=SubjectVisit._meta.label_lower,
            offstudy_model=SubjectOffstudy._meta.label_lower,
            death_report_model=DeathReport._meta.label_lower,
            enrollment_model=Enrollment._meta.label_lower,
            disenrollment_model='blah')


@tag('visit')
class TestVisitSchedule2(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model=SubjectVisit,
            offstudy_model=SubjectOffstudy,
            death_report_model=DeathReport)

        self.schedule = Schedule(
            name='schedule',
            enrollment_model=Enrollment._meta.label_lower,
            disenrollment_model=Disenrollment._meta.label_lower)

        self.schedule2 = Schedule(
            name='schedule_two',
            enrollment_model=EnrollmentTwo._meta.label_lower,
            disenrollment_model=DisenrollmentTwo._meta.label_lower)

        self.schedule3 = Schedule(
            name='schedule_three',
            enrollment_model=EnrollmentThree._meta.label_lower,
            disenrollment_model=DisenrollmentThree._meta.label_lower)

    def test_visit_schedule_add_schedule(self):
        try:
            self.visit_schedule.add_schedule(self.schedule)
        except AlreadyRegisteredSchedule:
            self.fail('AlreadyRegisteredSchedule unexpectedly raised.')

    def test_visit_schedule_cannot_add_to_wrong_visit_schedule(self):
        """Asserts cannot add schedule to wrong visit_schedule_name.
        """
        self.visit_schedule.add_schedule(self.schedule)
        self.assertRaises(ValidatorMetaValueError,
                          self.visit_schedule.add_schedule, self.schedule2)

    def test_visit_already_added_to_schedule(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.assertRaises(AlreadyRegisteredSchedule,
                          self.visit_schedule.add_schedule, self.schedule)

    def test_visit_schedule_get_schedule_by_name(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        schedule = self.visit_schedule.get_schedule(schedule_name='schedule')
        self.assertEqual(schedule.name, 'schedule')
        schedule = self.visit_schedule.get_schedule(
            schedule_name='schedule_three')
        self.assertEqual(schedule.name, 'schedule_three')

    def test_visit_schedule_get_schedule_by_model(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        schedule = self.visit_schedule.get_schedule(model=Enrollment)
        self.assertEqual(schedule.name, 'schedule')
        schedule = self.visit_schedule.get_schedule(model=EnrollmentThree)
        self.assertEqual(schedule.name, 'schedule_three')

    def test_visit_schedule_get_schedules(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        schedules = self.visit_schedule.get_schedules()
        self.assertEqual(
            list(schedules.keys()), [
                'schedule', 'schedule_three'])

    def test_visit_schedule_get_schedules_by_name(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        schedules = self.visit_schedule.get_schedules(schedule_name='schedule')
        self.assertEqual(list(schedules.keys()), ['schedule'])

    def test_visit_schedule_get_schedule_bad_name(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        self.assertRaises(
            VisitScheduleError,
            self.visit_schedule.get_schedules, schedule_name='blah')

    def test_crfs_unique_show_order(self):
        crfs = (
            Crf(show_order=10, model='edc_example.CrfOne'),
            Crf(show_order=20, model='edc_example.CrfTwo'),
            Crf(show_order=20, model='edc_example.CrfThree'),
        )
        self.assertRaises(
            FormsCollectionError,
            self.schedule.add_visit, code='1000', timepoint=0, crfs=crfs)


@tag('visit')
class TestVisitSchedule3(TestCase):

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

        self.visit_schedule.add_schedule(self.schedule)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

    def test_can_create_disenrollment_with_enrollment(self):
        Enrollment.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow())
        try:
            Disenrollment.objects.create(
                subject_identifier='1',
                disenrollment_datetime=get_utcnow())
        except Exception as e:
            self.fail(f'Exception unexpectedly raised. Got {e}.')

    def test_cannot_create_disenrollment_without_enrollment(self):
        self.assertRaises(
            DisenrollmentError,
            Disenrollment.objects.create,
            subject_identifier='111111')

    def test_cannot_create_disenrollment_before_enrollment(self):
        Enrollment.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow() - relativedelta(months=1))
        self.assertRaises(
            DisenrollmentError,
            Disenrollment.objects.create,
            subject_identifier='1',
            disenrollment_datetime=get_utcnow() - relativedelta(months=2))

    def test_cannot_create_disenrollment_before_last_visit(self):
        Enrollment.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow() - relativedelta(months=1))
        SubjectVisit.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow() + relativedelta(months=1))
        self.assertRaises(
            DisenrollmentError,
            Disenrollment.objects.create,
            subject_identifier='1',
            disenrollment_datetime=get_utcnow())

    def test_can_create_disenrollment_without_last_visit(self):
        Enrollment.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow() - relativedelta(months=1))
        try:
            Disenrollment.objects.create(
                subject_identifier='1',
                disenrollment_datetime=get_utcnow())
        except DisenrollmentError:
            self.fail('DisenrollmentError unexpectedly raised')

    def test_enrollment_model_knows_schedule_name(self):
        """Assert if schedule name provided on meta, does not need to
        be provided explicitly.
        """
        obj = Enrollment.objects.create(
            subject_identifier='111111', is_eligible=True)
        self.assertEqual(obj.visit_schedule_name, self.visit_schedule.name)
        self.assertEqual(obj.schedule_name, self.schedule.name)

    def test_cannot_enroll_if_visit_schedule_not_registered(self):
        self.assertRaises(EnrollmentModelError, EnrollmentTwo.objects.create)

    def test_cannot_enroll_if_schedule_not_added(self):
        self.assertRaises(
            EnrollmentModelError, EnrollmentThree.objects.create)
