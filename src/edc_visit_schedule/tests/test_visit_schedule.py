from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_base.utils import get_utcnow
from uuid import uuid4

from ..offschedule_validator import OffScheduleError
from ..model_mixins import OnScheduleModelError
from ..schedule import Schedule, ScheduleAppointmentModelError
from ..site_visit_schedules import site_visit_schedules
from ..validator import ValidatorMetaValueError
from ..visit import Crf, FormsCollectionError
from ..visit_schedule import VisitSchedule, VisitScheduleError, ModelsCollectionError
from ..visit_schedule import VisitScheduleNameError, AlreadyRegisteredSchedule
from .models import OnSchedule, OnScheduleThree, OnScheduleTwo, OffSchedule
from .models import SubjectVisit, BadMetaModel2, BadMetaModel3
from ..offschedule_validator import OffScheduleValidator


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
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.deathreport',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

    def test_visit_schedule_repr(self):
        """Asserts repr evaluates correctly.
        """
        v = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.deathreport',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')
        self.assertTrue(v.__repr__())

    def test_visit_schedule_validates(self):
        visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')
        try:
            visit_schedule.validate()
        except VisitScheduleError as e:
            self.fail(f'VisitScheduleError unepectedly raised {e}')

    def test_visit_schedule_bad_onschedule_model_raises_on_validate(self):
        visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='blah.blah',
            offschedule_model='edc_visit_schedule.offschedule')
        self.assertRaises(
            ModelsCollectionError,
            visit_schedule.validate)

    def test_visit_schedule_bad_offschedule_model_raises_on_validate(self):
        visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='blah')
        self.assertRaises(
            ModelsCollectionError,
            visit_schedule.validate)


class TestVisitSchedule2(TestCase):

    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.subjectvisit',
            offstudy_model='edc_visit_schedule.subjectoffstudy',
            death_report_model='edc_visit_schedule.deathreport')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule',
            appointment_model='edc_appointment.appointment')

        self.schedule2 = Schedule(
            name='schedule_two',
            onschedule_model='edc_visit_schedule.onscheduletwo',
            offschedule_model='edc_visit_schedule.offscheduletwo',
            appointment_model='edc_appointment.appointment')

        self.schedule3 = Schedule(
            name='schedule_three',
            onschedule_model='edc_visit_schedule.onschedulethree',
            offschedule_model='edc_visit_schedule.offschedulethree',
            appointment_model='myapp.appointment')

    def test_visit_schedule_add_schedule(self):
        try:
            self.visit_schedule.add_schedule(self.schedule)
        except AlreadyRegisteredSchedule:
            self.fail('AlreadyRegisteredSchedule unexpectedly raised.')

    @override_settings(DEFAULT_APPOINTMENT_MODEL=None)
    def test_visit_schedule_add_schedule_without_appointment_model(self):
        self.assertRaises(
            ScheduleAppointmentModelError,
            Schedule,
            name='schedule_bad',
            onschedule_model='edc_visit_schedule.onschedule',
            offschedule_model='edc_visit_schedule.offschedule')

    @override_settings(DEFAULT_APPOINTMENT_MODEL='myapp.appointment')
    def test_visit_schedule_add_schedule_without_appointment_model_and_settings(self):
        try:
            Schedule(
                name='schedule_bad',
                onschedule_model='edc_visit_schedule.onschedule',
                offschedule_model='edc_visit_schedule.offschedule')
        except ScheduleAppointmentModelError:
            self.fail()

    def test_visit_schedule_add_schedule_with_appointment_model(self):
        self.visit_schedule.add_schedule(self.schedule3)
        for schedule in self.visit_schedule.schedules.values():
            self.assertEqual(schedule.appointment_model, 'myapp.appointment')

    def test_visit_schedule_cannot_add_to_wrong_visit_schedule(self):
        """Asserts cannot add schedule to wrong model.visit_schedule_name.
        """
        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule2)
        self.assertRaises(
            ValidatorMetaValueError,
            self.visit_schedule.validate)

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
        schedule = self.visit_schedule.get_schedule(
            model='edc_visit_schedule.onschedule')
        self.assertEqual(schedule.name, 'schedule')
        schedule = self.visit_schedule.get_schedule(
            model='edc_visit_schedule.onschedulethree')
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


class TestVisitSchedule3(TestCase):

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

        self.visit_schedule.add_schedule(self.schedule)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

    def test_can_create_offschedule_with_onschedule(self):
        consent_identifier = uuid4()
        OnSchedule.objects.create(
            subject_identifier='1',
            consent_identifier=consent_identifier,
            onschedule_datetime=get_utcnow())
        OffScheduleValidator(
            subject_identifier='1',
            offschedule_datetime=get_utcnow(),
            visit_schedule_name='visit_schedule',
            schedule_name='schedule',
        )
        try:
            OffSchedule.objects.create(
                subject_identifier='1',
                consent_identifier=consent_identifier,
                offschedule_datetime=get_utcnow())
        except Exception as e:
            self.fail(f'Exception unexpectedly raised. Got {e}.')

    def test_cannot_create_offschedule_without_onschedule(self):
        self.assertRaises(
            OffScheduleError,
            OffSchedule.objects.create,
            subject_identifier='111111')

    def test_cannot_create_offschedule_before_onschedule(self):
        OnSchedule.objects.create(
            subject_identifier='1',
            consent_identifier=uuid4(),
            onschedule_datetime=get_utcnow() - relativedelta(months=1))
        self.assertRaises(
            OffScheduleError,
            OffSchedule.objects.create,
            subject_identifier='1',
            offschedule_datetime=get_utcnow() - relativedelta(months=2))

    def test_cannot_create_offschedule_before_last_visit(self):
        OnSchedule.objects.create(
            subject_identifier='1',
            consent_identifier=uuid4(),
            onschedule_datetime=get_utcnow() - relativedelta(months=1))
        SubjectVisit.objects.create(
            subject_identifier='1',
            report_datetime=get_utcnow() + relativedelta(months=1))
        self.assertRaises(
            OffScheduleError,
            OffSchedule.objects.create,
            subject_identifier='1',
            offschedule_datetime=get_utcnow())

    def test_can_create_offschedule_without_last_visit(self):
        consent_identifier = uuid4()
        OnSchedule.objects.create(
            subject_identifier='1',
            consent_identifier=consent_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(months=1))
        try:
            OffSchedule.objects.create(
                subject_identifier='1',
                consent_identifier=consent_identifier,
                offschedule_datetime=get_utcnow())
        except OffScheduleError:
            self.fail('OffScheduleError unexpectedly raised')

    def test_onschedule_model_knows_schedule_name(self):
        """Assert if schedule name provided on meta, does not need to
        be provided explicitly.
        """
        obj = OnSchedule.objects.create(
            subject_identifier='111111',
            consent_identifier=uuid4())
        self.assertEqual(obj.visit_schedule_name, self.visit_schedule.name)
        self.assertEqual(obj.schedule_name, self.schedule.name)

    def test_cannot_put_on_schedule_if_visit_schedule_not_registered(self):
        self.assertRaises(VisitScheduleError, OnScheduleTwo.objects.create)

    def test_cannot_put_on_schedule_if_schedule_not_added(self):
        self.assertRaises(
            VisitScheduleError, OnScheduleThree.objects.create)

    def test_visit_schedule_name_not_set(self):
        self.assertRaises(
            OnScheduleModelError, BadMetaModel2.objects.create)

    def test_consent_model_not_set(self):
        self.assertRaises(
            OnScheduleModelError, BadMetaModel3.objects.create)
