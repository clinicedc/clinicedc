import arrow
import pytz

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow

from ..constants import OFF_SCHEDULE, ON_SCHEDULE
from ..models import SubjectScheduleHistory
from ..site_visit_schedules import site_visit_schedules, RegistryNotLoaded
from .models import OnSchedule, OffSchedule, SubjectVisit, CrfOne
from .models import OnScheduleFive, OnScheduleSeven, OffScheduleFive
from .models import OnScheduleSix, OffScheduleSix, OffScheduleSeven, BadOffSchedule1
from .visit_schedule import visit_schedule, visit_schedule5, visit_schedule6
from .visit_schedule import visit_schedule7


class TestModels(SiteTestCaseMixin, TestCase):
    def setUp(self):
        import_holidays()
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

    def test_str(self):
        obj = OnSchedule.objects.create(subject_identifier="1234")
        self.assertIn("1234", str(obj))
        self.assertEqual(obj.natural_key(), ("1234",))
        self.assertEqual(
            obj, OnSchedule.objects.get_by_natural_key(subject_identifier="1234")
        )

    def test_str_offschedule(self):
        OnSchedule.objects.create(subject_identifier="1234")
        obj = OffSchedule.objects.create(subject_identifier="1234")
        self.assertIn("1234", str(obj))
        self.assertEqual(obj.natural_key(), ("1234",))
        self.assertEqual(
            obj, OffSchedule.objects.get_by_natural_key(subject_identifier="1234")
        )

    def test_offschedule_custom_field_datetime(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule5)

        OnScheduleFive.objects.create(
            subject_identifier="1234",
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = get_utcnow() - relativedelta(years=1)
        obj = OffScheduleFive.objects.create(
            subject_identifier="1234", my_offschedule_datetime=offschedule_datetime
        )
        self.assertEqual(obj.my_offschedule_datetime, offschedule_datetime)
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_offschedule_custom_field_date(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule6)

        OnScheduleSix.objects.create(
            subject_identifier="1234",
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = arrow.Arrow.fromdate(
            (get_utcnow() - relativedelta(years=1)).date()
        )
        obj = OffScheduleSix.objects.create(
            subject_identifier="1234", my_offschedule_date=offschedule_datetime.date()
        )
        self.assertEqual(obj.my_offschedule_date, offschedule_datetime.date())
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_bad_offschedule1(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule6)

        OnScheduleSix.objects.create(
            subject_identifier="1234",
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        self.assertRaises(
            ImproperlyConfigured,
            BadOffSchedule1.objects.create,
            subject_identifier="1234",
            my_offschedule_date=get_utcnow(),
        )

    def test_offschedule_no_meta_defaults_offschedule_field(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule7)

        OnScheduleSeven.objects.create(
            subject_identifier="1234",
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = get_utcnow()
        obj = OffScheduleSeven.objects.create(
            subject_identifier="1234", offschedule_datetime=offschedule_datetime
        )

        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_onschedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded, OnSchedule.objects.create, subject_identifier="1234"
        )

    def test_offschedule_raises(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded, OffSchedule.objects.create, subject_identifier="1234"
        )

    def test_on_offschedule(self):
        OnSchedule.objects.create(
            subject_identifier="1234",
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc),
        )
        history_obj = SubjectScheduleHistory.objects.get(subject_identifier="1234")
        self.assertEqual(history_obj.schedule_status, ON_SCHEDULE)
        OffSchedule.objects.create(
            subject_identifier="1234", offschedule_datetime=get_utcnow()
        )
        history_obj = SubjectScheduleHistory.objects.get(subject_identifier="1234")
        self.assertEqual(history_obj.schedule_status, OFF_SCHEDULE)

    def test_history(self):
        OnSchedule.objects.create(
            subject_identifier="1234",
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc),
        )
        OffSchedule.objects.create(
            subject_identifier="1234", offschedule_datetime=get_utcnow()
        )
        obj = SubjectScheduleHistory.objects.get(subject_identifier="1234")
        self.assertEqual(
            obj.natural_key(),
            (obj.subject_identifier, obj.visit_schedule_name, obj.schedule_name),
        )
        self.assertEqual(
            SubjectScheduleHistory.objects.get_by_natural_key(
                obj.subject_identifier, obj.visit_schedule_name, obj.schedule_name
            ),
            obj,
        )

    def test_crf(self):
        """Assert can enter a CRF.
        """

        OnSchedule.objects.create(
            subject_identifier="1234",
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc),
        )
        appointments = Appointment.objects.all()
        self.assertEqual(appointments.count(), 4)
        appointment = Appointment.objects.all().order_by("appt_datetime").first()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            subject_identifier="1234",
        )
        CrfOne.objects.create(
            subject_visit=subject_visit, report_datetime=appointment.appt_datetime
        )
        OffSchedule.objects.create(
            subject_identifier="1234", offschedule_datetime=appointment.appt_datetime
        )
        self.assertEqual(Appointment.objects.all().count(), 1)

    def test_onschedules_manager(self):
        """Assert can enter a CRF.
        """

        onschedule = OnSchedule.objects.create(
            subject_identifier="1234",
            onschedule_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc),
        )

        history = SubjectScheduleHistory.objects.onschedules(subject_identifier="1234")
        self.assertEqual([onschedule], [obj for obj in history])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234", report_datetime=get_utcnow()
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234",
            report_datetime=datetime(2017, 11, 30, 0, 0, 0, 0, pytz.utc),
        )
        self.assertEqual(0, len(onschedules))

        # add offschedule
        OffSchedule.objects.create(
            subject_identifier="1234",
            offschedule_datetime=datetime(2017, 12, 15, 0, 0, 0, 0, pytz.utc),
        )

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234",
            report_datetime=datetime(2017, 11, 30, 0, 0, 0, 0, pytz.utc),
        )
        self.assertEqual(0, len(onschedules))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234",
            report_datetime=datetime(2017, 12, 1, 0, 0, 0, 0, pytz.utc),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234",
            report_datetime=datetime(2017, 12, 2, 0, 0, 0, 0, pytz.utc),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier="1234",
            report_datetime=datetime(2018, 1, 1, 0, 0, 0, 0, pytz.utc),
        )
        self.assertEqual(0, len(onschedules))

    def test_natural_key(self):
        obj = OnSchedule.objects.create(subject_identifier="1234")
        self.assertEqual(obj.natural_key(), ("1234",))
        obj = OffSchedule.objects.create(subject_identifier="1234")
        self.assertEqual(obj.natural_key(), ("1234",))
