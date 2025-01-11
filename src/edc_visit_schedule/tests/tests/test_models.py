from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_visit_schedule.constants import OFF_SCHEDULE, ON_SCHEDULE
from edc_visit_schedule.models import SubjectScheduleHistory
from edc_visit_schedule.site_visit_schedules import (
    RegistryNotLoaded,
    site_visit_schedules,
)
from visit_schedule_app.models import (
    BadOffSchedule1,
    CrfOne,
    OffSchedule,
    OffScheduleFive,
    OffScheduleSeven,
    OffScheduleSix,
    OnSchedule,
    OnScheduleFive,
    OnScheduleSeven,
    OnScheduleSix,
    SubjectConsent,
    SubjectVisit,
)
from visit_schedule_app.visit_schedule import (
    visit_schedule,
    visit_schedule5,
    visit_schedule6,
    visit_schedule7,
)


@time_machine.travel(datetime(2019, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    SITE_ID=30,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestModels(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}

        self.subject_identifier = "1234"
        site_consents.registry = {}
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        self.consent_v1 = ConsentDefinition(
            "visit_schedule_app.subjectconsentv1",
            version="1",
            start=ResearchProtocolConfig().study_open_datetime,
            end=ResearchProtocolConfig().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.register(self.consent_v1)
        visit_schedule.schedules["schedule"].consent_definitions = [self.consent_v1]
        site_visit_schedules.register(visit_schedule)

    def test_str(self):
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertIn(self.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        self.assertEqual(
            obj,
            OnSchedule.objects.get_by_natural_key(subject_identifier=self.subject_identifier),
        )

    def test_str_offschedule(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)
        OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        obj = OffSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertIn(self.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        self.assertEqual(
            obj,
            OffSchedule.objects.get_by_natural_key(subject_identifier=self.subject_identifier),
        )
        traveller.stop()

    def test_offschedule_custom_field_datetime(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        visit_schedule5.schedules["schedule5"].consent_definitions = [self.consent_v1]
        site_visit_schedules.register(visit_schedule5)

        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
        )
        OnScheduleFive.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        offschedule_datetime = get_utcnow()
        obj = OffScheduleFive.objects.create(
            subject_identifier=self.subject_identifier,
            my_offschedule_datetime=offschedule_datetime,
        )
        self.assertEqual(obj.my_offschedule_datetime, offschedule_datetime)
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)
        traveller.stop()

    def test_offschedule_custom_field_date(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        visit_schedule6.schedules["schedule6"].consent_definitions = [self.consent_v1]
        site_visit_schedules.register(visit_schedule6)

        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
        )
        OnScheduleSix.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        offschedule_datetime = get_utcnow()

        try:
            OffScheduleSix.objects.create(
                subject_identifier=self.subject_identifier,
                my_offschedule_date=offschedule_datetime.date(),
            )
        except ImproperlyConfigured:
            pass
        else:
            self.fail("ImproperlyConfigured not raised")
        traveller.stop()

    def test_bad_offschedule1(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        visit_schedule6.schedules["schedule6"].consent_definitions = [self.consent_v1]
        site_visit_schedules.register(visit_schedule6)

        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        OnScheduleSix.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        offschedule_datetime = get_utcnow()

        self.assertRaises(
            ImproperlyConfigured,
            BadOffSchedule1.objects.create,
            subject_identifier=self.subject_identifier,
            my_offschedule_date=offschedule_datetime,
        )
        traveller.stop()

    def test_offschedule_no_meta_defaults_offschedule_field(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        visit_schedule7.schedules["schedule7"].consent_definitions = [self.consent_v1]
        site_visit_schedules.register(visit_schedule7)

        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
        )
        OnScheduleSeven.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        offschedule_datetime = get_utcnow()
        obj = OffScheduleSeven.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=offschedule_datetime,
        )

        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)
        traveller.stop()

    def test_onschedule(self):
        """Asserts cannot access without site_visit_schedule loaded."""
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OnSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )
        traveller.stop()

    def test_offschedule_raises(self):
        """Asserts cannot access without site_visit_schedule loaded."""
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )
        traveller.stop()

    def test_on_offschedule(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        consent_datetime = get_utcnow() + relativedelta(days=10)
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=consent_datetime,
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=consent_datetime,
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, ON_SCHEDULE)
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, OFF_SCHEDULE)
        traveller.stop()

    def test_history(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        obj = SubjectScheduleHistory.objects.get(subject_identifier=self.subject_identifier)
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
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        self.assertEqual(appointments.count(), 4)
        appointment = Appointment.objects.all().order_by("appt_datetime").first()
        traveller.stop()

        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(
            subject_visit=subject_visit, report_datetime=appointment.appt_datetime
        )
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=appointment.appt_datetime,
        )
        self.assertEqual(Appointment.objects.all().count(), 1)
        traveller.stop()

    def test_onschedules_manager(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
        )
        onschedule_datetime = get_utcnow()
        onschedule = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        history = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual([onschedule], [obj for obj in history])
        traveller.stop()

        traveller = time_machine.travel(self.study_open_datetime + relativedelta(months=3))
        traveller.start()
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier, report_datetime=get_utcnow()
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(months=4),
        )
        self.assertEqual(0, len(onschedules))

        # add offschedule
        traveller = time_machine.travel(self.study_open_datetime + relativedelta(months=5))
        traveller.start()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() + relativedelta(days=1),
        )
        self.assertEqual(0, len(onschedules))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(days=1),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() - relativedelta(months=1),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() + relativedelta(months=1),
        )
        self.assertEqual(0, len(onschedules))

    def test_natural_key(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(months=3),
        )
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        traveller.stop()
        traveller = time_machine.travel(self.study_open_datetime + relativedelta(years=1))
        traveller.start()
        obj = OffSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        traveller.stop()
