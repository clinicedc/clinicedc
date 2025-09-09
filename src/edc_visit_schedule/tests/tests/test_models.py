from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings, tag, TestCase

from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.constants import OFF_SCHEDULE, ON_SCHEDULE
from edc_visit_schedule.models import OnSchedule, SubjectScheduleHistory
from edc_visit_schedule.site_visit_schedules import (
    RegistryNotLoaded,
    site_visit_schedules,
)
from edc_visit_tracking.constants import SCHEDULED
from tests.action_items import register_actions
from tests.consents import consent5_v1, consent6_v1, consent7_v1, consent_v1
from tests.helper import Helper
from tests.models import (
    BadOffSchedule1,
    CrfOne,
    OffSchedule,
    OffScheduleFive,
    OffScheduleSeven,
    OffScheduleSix,
    OnScheduleSix,
    SubjectVisit,
)
from tests.sites import all_sites
from tests.visit_schedules.visit_schedule import get_visit_schedule
from tests.visit_schedules.visit_schedule_visitschedule import (
    visit_schedule5,
    visit_schedule6,
    visit_schedule7,
)


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(
    SITE_ID=30,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestModels(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_consents.register(consent5_v1)
        site_consents.register(consent6_v1)
        site_consents.register(consent7_v1)
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        site_visit_schedules.register(visit_schedule5)
        site_visit_schedules.register(visit_schedule6)
        site_visit_schedules.register(visit_schedule7)
        if not site_visit_schedules.loaded:
            raise ValueError(f"site_visit_schedules not loaded. See {cls}.")

    def setUp(self):
        site_visit_schedules.loaded = True
        self.helper = Helper()

    def test_str(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            report_datetime=get_utcnow(),
            consent_definition=consent_v1,
        )
        obj = OnSchedule.objects.get(subject_identifier=consent.subject_identifier)
        self.assertIn(consent.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (consent.subject_identifier,))
        self.assertEqual(
            obj,
            OnSchedule.objects.get_by_natural_key(
                subject_identifier=consent.subject_identifier
            ),
        )

    def test_str_offschedule(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            report_datetime=get_utcnow(),
            consent_definition=consent_v1,
        )
        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        obj = OffSchedule.objects.create(subject_identifier=consent.subject_identifier)
        self.assertIn(consent.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (consent.subject_identifier,))
        self.assertEqual(
            obj,
            OffSchedule.objects.get_by_natural_key(
                subject_identifier=consent.subject_identifier
            ),
        )
        traveller.stop()

    def test_offschedule_custom_field_datetime(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule5",
            schedule_name="schedule5",
            consent_definition=consent5_v1,
            report_datetime=get_utcnow(),
        )

        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        offschedule_datetime = get_utcnow()
        obj = OffScheduleFive.objects.create(
            subject_identifier=consent.subject_identifier,
            my_offschedule_datetime=offschedule_datetime,
        )
        self.assertEqual(obj.my_offschedule_datetime, offschedule_datetime)
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)
        traveller.stop()

    def test_offschedule_custom_field_date(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule6",
            schedule_name="schedule6",
            consent_definition=consent6_v1,
            report_datetime=get_utcnow(),
        )

        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        offschedule_datetime = get_utcnow()
        try:
            OffScheduleSix.objects.create(
                subject_identifier=consent.subject_identifier,
                my_offschedule_date=offschedule_datetime.date(),
            )
        except ImproperlyConfigured:
            pass
        else:
            self.fail("ImproperlyConfigured not raised")
        traveller.stop()

    def test_bad_offschedule1(self):
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule6",
            schedule_name="schedule6",
            consent_definition=consent6_v1,
            report_datetime=get_utcnow(),
        )
        traveller = time_machine.travel(
            subject_consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        offschedule_datetime = get_utcnow()

        self.assertRaises(
            ImproperlyConfigured,
            BadOffSchedule1.objects.create,
            subject_identifier=subject_consent.subject_identifier,
            my_offschedule_date=offschedule_datetime,
        )
        traveller.stop()

    def test_offschedule_no_meta_defaults_offschedule_field(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule7",
            schedule_name="schedule7",
            consent_definition=consent7_v1,
            report_datetime=get_utcnow(),
        )
        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        offschedule_datetime = get_utcnow()
        obj = OffScheduleSeven.objects.create(
            subject_identifier=consent.subject_identifier,
            offschedule_datetime=offschedule_datetime,
        )

        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)
        traveller.stop()

    def test_onschedule(self):
        """Asserts cannot access without site_visit_schedule loaded."""
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule6",
            schedule_name="schedule6",
            consent_definition=consent6_v1,
            report_datetime=get_utcnow(),
        )
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OnScheduleSix.objects.put_on_schedule,
            subject_identifier=consent.consent_datetime,
        )

    def test_offschedule_raises(self):
        """Asserts cannot access without site_visit_schedule loaded."""
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule6",
            schedule_name="schedule6",
            consent_definition=consent6_v1,
            report_datetime=get_utcnow(),
        )
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OffScheduleSix.objects.create,
            subject_identifier=consent.consent_datetime,
        )

    def test_on_offschedule(self):
        traveller = time_machine.travel(
            datetime(2025, 6, 21, 8, 00, tzinfo=ZoneInfo("UTC"))
        )
        traveller.start()
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule7",
            schedule_name="schedule7",
            consent_definition=consent7_v1,
            report_datetime=get_utcnow(),
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=consent.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, ON_SCHEDULE)
        traveller.stop()

        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        OffScheduleSeven.objects.create(
            subject_identifier=consent.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=consent.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, OFF_SCHEDULE)
        traveller.stop()

    def test_history(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent_v1,
            report_datetime=get_utcnow(),
        )
        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        OffSchedule.objects.create(
            subject_identifier=consent.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        obj = SubjectScheduleHistory.objects.get(
            subject_identifier=consent.subject_identifier
        )
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
        traveller.stop()

    def test_crf(self):
        """Assert can enter a CRF."""
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent_v1,
            report_datetime=get_utcnow(),
        )
        appointments = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )
        self.assertEqual(appointments.count(), 2)
        appointment = Appointment.objects.all().order_by("appt_datetime").first()

        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            subject_identifier=subject_consent.subject_identifier,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(
            subject_visit=subject_visit, report_datetime=appointment.appt_datetime
        )
        OffSchedule.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            offschedule_datetime=appointment.appt_datetime,
        )
        self.assertEqual(Appointment.objects.all().count(), 1)
        traveller.stop()

    def test_onschedules_manager(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent_v1,
            report_datetime=get_utcnow(),
        )
        onschedule = OnSchedule.objects.get(
            subject_identifier=consent.subject_identifier
        )
        history = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier
        )
        self.assertEqual([onschedule], [obj for obj in history])

        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(months=3)
        )
        traveller.start()
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier, report_datetime=get_utcnow()
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(months=4),
        )
        self.assertEqual(0, len(onschedules))

        # add offschedule
        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(months=5)
        )
        traveller.start()
        OffSchedule.objects.create(
            subject_identifier=consent.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier,
            report_datetime=get_utcnow() + relativedelta(days=1),
        )
        self.assertEqual(0, len(onschedules))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(days=1),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(months=1),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=consent.subject_identifier,
            report_datetime=get_utcnow() + relativedelta(months=1),
        )
        self.assertEqual(0, len(onschedules))

    def test_natural_key(self):
        consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent_v1,
            report_datetime=get_utcnow(),
        )
        obj = OnSchedule.objects.get(subject_identifier=consent.subject_identifier)
        self.assertEqual(obj.natural_key(), (consent.subject_identifier,))

        traveller = time_machine.travel(
            consent.consent_datetime + relativedelta(years=1)
        )
        traveller.start()
        obj = OffSchedule.objects.create(subject_identifier=consent.subject_identifier)
        self.assertEqual(obj.natural_key(), (consent.subject_identifier,))
        traveller.stop()
