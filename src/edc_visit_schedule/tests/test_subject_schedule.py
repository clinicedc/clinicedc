from django.test import TestCase, tag
from django.core.exceptions import ObjectDoesNotExist
from uuid import uuid4

from ..subject_schedule import SubjectSchedule, SubjectScheduleError
from ..subject_schedule_history import SubjectScheduleHistory
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..visit_schedule import VisitSchedule
from .models import OnScheduleTwo, SubjectConsent, OnSchedule, OffSchedule


class TestSubjectSchedule(TestCase):

    def setUp(self):
        site_visit_schedules._registry = {}
        self.visit_schedule = VisitSchedule(
            name='visit_schedule',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport')

        self.schedule = Schedule(
            name='schedule',
            onschedule_model='edc_visit_schedule.OnSchedule',
            offschedule_model='edc_visit_schedule.OffSchedule')
        self.schedule3 = Schedule(
            name='schedule_three',
            onschedule_model='edc_visit_schedule.OnScheduleThree',
            offschedule_model='edc_visit_schedule.OffScheduleThree')

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules.register(self.visit_schedule)

        self.visit_schedule_two = VisitSchedule(
            name='visit_schedule_two',
            verbose_name='Visit Schedule Two',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport')

        self.schedule_two_1 = Schedule(
            name='schedule_two',
            onschedule_model='edc_visit_schedule.OnScheduleTwo',
            offschedule_model='edc_visit_schedule.OffScheduleTwo')
        self.schedule_two_2 = Schedule(
            name='schedule_four',
            onschedule_model='edc_visit_schedule.OnScheduleFour',
            offschedule_model='edc_visit_schedule.OffScheduleFour')

        self.visit_schedule_two.add_schedule(self.schedule_two_1)
        self.visit_schedule_two.add_schedule(self.schedule_two_2)
        site_visit_schedules.register(self.visit_schedule_two)
        self.subject_identifier = '111111'
        obj = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier)
        self.consent_identifier = obj.consent_identifier

    @tag('1')
    def test_history(self):
        history = SubjectScheduleHistory()
        self.assertFalse(history.history)

    @tag('1')
    def test_history_not_onschedule(self):
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertFalse(history.history)

    @tag('1')
    def test_get_onschedule_but_empty(self):
        """Asserts returns an empty list if not on-schedule.
        """
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertFalse(history.history)

    @tag('1')
    def test_get_onschedule(self):
        """Asserts returns an onschedule instance if on-schedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model_cls=OnScheduleTwo,
            subject_identifier=self.subject_identifier,
            consent_identifier=uuid4())
        obj = subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            history.history, [obj])

    def test_get_onschedule_many(self):
        """Asserts returns an empty list if not on-schedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        obj1 = subject_schedule.put_on_schedule()
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onschedulefour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        obj2 = subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertEqual(history.history, [obj1, obj2])

    def test_schedules(self):
        """Asserts returns one schedule if one onschedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            [s.name for s in history.schedules.values()],
            ['schedule_two'])

    def test_schedules_many(self):
        """Asserts returns two schedules if two onschedule models.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onschedulefour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            [s.name for s in history.schedules.values()],
            ['schedule_four', 'schedule_two'])

    def test_gets_correct_history_if_many_others(self):
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        obj = subject_schedule.put_on_schedule()
        for i in range(0, 5):
            SubjectConsent.objects.create(subject_identifier=str(i))
            SubjectSchedule(
                onschedule_model='edc_visit_schedule.onschedulefour',
                subject_identifier=str(i),
                consent_identifier=uuid4())
            subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier)
        self.assertEqual(history.history, [obj])

    def test_get_onschedule5(self):
        """Asserts returns None for unknown schedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onschedulefour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        self.assertRaises(
            SiteVisitScheduleError,
            SubjectScheduleHistory,
            subject_identifier=self.subject_identifier,
            visit_schedule_name='blah')

    def test_get_onschedule6(self):
        """Asserts returns the correct instances for the schedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onschedulefour',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        history = SubjectScheduleHistory(
            subject_identifier=self.subject_identifier,
            schedule_name='schedule_four')
        self.assertEqual(len(history.history), 1)

    def test_raises_if_no_consent(self):
        """Asserts raises if no consent for this subject.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier='ABCDEF',
            consent_identifier=uuid4())
        self.assertRaises(
            SubjectScheduleError,
            subject_schedule.put_on_schedule)

    def test_multpile_consents(self):
        """Asserts does not raise if more than one consent
        for this subject
        """

        subject_identifier = 'ABCDEF'
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            version='1')
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            version='2')
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=subject_identifier,
            consent_identifier=uuid4())
        try:
            subject_schedule.put_on_schedule()
        except SubjectScheduleError:
            self.fail('SubjectScheduleError unexpectedly raised.')

    def test_resave(self):
        """Asserts returns the correct instances for the schedule.
        """
        subject_schedule = SubjectSchedule(
            onschedule_model='edc_visit_schedule.onscheduletwo',
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        subject_schedule.put_on_schedule()
        subject_schedule.resave()

    def test_put_on_schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name='visit_schedule')
        schedule = visit_schedule.schedules.get('schedule')
        self.assertRaises(
            ObjectDoesNotExist,
            OnSchedule.objects.get,
            subject_identifier=self.subject_identifier)
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        try:
            OnSchedule.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail('ObjectDoesNotExist unexpectedly raised')

    def test_take_off_schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name='visit_schedule')
        schedule = visit_schedule.schedules.get('schedule')
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        schedule.take_off_schedule(
            subject_identifier=self.subject_identifier,
            consent_identifier=self.consent_identifier)
        try:
            OffSchedule.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail('ObjectDoesNotExist unexpectedly raised')
