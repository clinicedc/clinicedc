import pytz

from datetime import datetime
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_base.tests import SiteTestCaseMixin
from edc_facility.import_holidays import import_holidays

from ..constants import OFF_SCHEDULE, ON_SCHEDULE
from ..models import SubjectScheduleHistory
from ..site_visit_schedules import site_visit_schedules, RegistryNotLoaded
from .models import OnSchedule, OffSchedule, SubjectVisit, CrfOne
from .visit_schedule import visit_schedule


class TestModels(SiteTestCaseMixin, TestCase):

    def setUp(self):
        import_holidays()
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

    def test_str(self):
        obj = OnSchedule.objects.create(subject_identifier='1234')
        self.assertIn('1234', str(obj))
        self.assertEqual(obj.natural_key(), ('1234', ))
        self.assertEqual(obj, OnSchedule.objects.get_by_natural_key(
            subject_identifier='1234'))

    def test_str_offschedule(self):
        OnSchedule.objects.create(
            subject_identifier='1234')
        obj = OffSchedule.objects.create(subject_identifier='1234')
        self.assertIn('1234', str(obj))
        self.assertEqual(obj.natural_key(), ('1234', ))
        self.assertEqual(obj, OffSchedule.objects.get_by_natural_key(
            subject_identifier='1234'))

    def test_onschedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OnSchedule.objects.create, subject_identifier='1234')

    def test_offschedule_raises(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OffSchedule.objects.create, subject_identifier='1234')

    def test_on_offschedule(self):
        OnSchedule.objects.create(
            subject_identifier='1234',
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc))
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier='1234')
        self.assertEqual(history_obj.schedule_status, ON_SCHEDULE)
        OffSchedule.objects.create(
            subject_identifier='1234',
            offschedule_datetime=get_utcnow())
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier='1234')
        self.assertEqual(history_obj.schedule_status, OFF_SCHEDULE)

    def test_history(self):
        OnSchedule.objects.create(
            subject_identifier='1234',
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc))
        OffSchedule.objects.create(
            subject_identifier='1234',
            offschedule_datetime=get_utcnow())
        obj = SubjectScheduleHistory.objects.get(
            subject_identifier='1234')
        self.assertEqual(
            obj.natural_key(),
            (obj.subject_identifier, obj.visit_schedule_name, obj.schedule_name))
        self.assertEqual(
            SubjectScheduleHistory.objects.get_by_natural_key(
                obj.subject_identifier, obj.visit_schedule_name, obj.schedule_name),
            obj)

    def test_crf(self):
        """Assert can enter a CRF.
        """
        OnSchedule.objects.create(
            subject_identifier='1234',
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc))
        self.assertEqual(Appointment.objects.all().count(), 4)
        appointment = Appointment.objects.all().order_by('appt_datetime').first()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            subject_identifier='1234')
        CrfOne.objects.create(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime)
        OffSchedule.objects.create(
            subject_identifier='1234',
            offschedule_datetime=appointment.appt_datetime)
        self.assertEqual(Appointment.objects.all().count(), 1)

    def test_onschedules_manager(self):
        """Assert can enter a CRF.
        """

        onschedule = OnSchedule.objects.create(
            subject_identifier='1234',
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc))

        history = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234')
        self.assertEqual([onschedule], [obj for obj in history])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234', report_datetime=get_utcnow())
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234',
            report_datetime=datetime(2017, 11, 30, 0, 0, 0, 0, pytz.utc))
        self.assertEqual(0, len(onschedules))

        # add offschedule
        OffSchedule.objects.create(
            subject_identifier='1234',
            offschedule_datetime=datetime(2017, 12, 15, 0, 0, 0, 0, pytz.utc))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234',
            report_datetime=datetime(2017, 11, 30, 0, 0, 0, 0, pytz.utc))
        self.assertEqual(0, len(onschedules))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234',
            report_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc))
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234',
            report_datetime=datetime(2017, 12, 2, 0, 0, 0, 0, pytz.utc))
        self.assertEqual([onschedule], [obj for obj in onschedules])
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier='1234',
            report_datetime=datetime(2018, 1, 1, 0, 0, 0, 0, pytz.utc))
        self.assertEqual(0, len(onschedules))

    def test_natural_key(self):
        obj = OnSchedule.objects.create(subject_identifier='1234')
        self.assertEqual(obj.natural_key(), ('1234', ))
        obj = OffSchedule.objects.create(subject_identifier='1234')
        self.assertEqual(obj.natural_key(), ('1234', ))
