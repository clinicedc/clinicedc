import arrow

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent import Consent
from edc_constants.constants import MALE, FEMALE
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.constants import OFF_SCHEDULE, ON_SCHEDULE
from edc_visit_schedule.models import SubjectScheduleHistory
from edc_visit_schedule.site_visit_schedules import (
    site_visit_schedules,
    RegistryNotLoaded,
)
from edc_visit_tracking.constants import SCHEDULED
from visit_schedule_app.models import (
    OnSchedule,
    OffSchedule,
    SubjectVisit,
    CrfOne,
    SubjectConsent,
    OnScheduleFive,
    OnScheduleSeven,
    OffScheduleFive,
    OnScheduleSix,
    OffScheduleSix,
    OffScheduleSeven,
    BadOffSchedule1,
)
from visit_schedule_app.visit_schedule import (
    visit_schedule,
    visit_schedule5,
    visit_schedule6,
    visit_schedule7,
)


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestModels(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        super().setUpClass()

    def setUp(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "visit_schedule_app.subjectvisit"
            }
        )
        v1_consent = Consent(
            "visit_schedule_app.subjectconsent",
            version="1",
            start=Protocol().study_open_datetime,
            end=Protocol().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        self.subject_identifier = "1234"
        site_consents.registry = {}
        site_consents.register(v1_consent)

    def test_str(self):
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertIn(self.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        self.assertEqual(
            obj,
            OnSchedule.objects.get_by_natural_key(
                subject_identifier=self.subject_identifier
            ),
        )

    def test_str_offschedule(self):
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)
        OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        obj = OffSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertIn(self.subject_identifier, str(obj))
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        self.assertEqual(
            obj,
            OffSchedule.objects.get_by_natural_key(
                subject_identifier=self.subject_identifier
            ),
        )

    def test_offschedule_custom_field_datetime(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule5)

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
        )
        OnScheduleFive.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = get_utcnow() - relativedelta(years=1)
        obj = OffScheduleFive.objects.create(
            subject_identifier=self.subject_identifier,
            my_offschedule_datetime=offschedule_datetime,
        )
        self.assertEqual(obj.my_offschedule_datetime, offschedule_datetime)
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_offschedule_custom_field_date(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule6)

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
        )
        OnScheduleSix.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = arrow.Arrow.fromdate(
            (get_utcnow() - relativedelta(years=1)).date()
        )
        obj = OffScheduleSix.objects.create(
            subject_identifier=self.subject_identifier,
            my_offschedule_date=offschedule_datetime.date(),
        )
        self.assertEqual(obj.my_offschedule_date, offschedule_datetime.date())
        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_bad_offschedule1(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule6)

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
        )
        OnScheduleSix.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        self.assertRaises(
            ImproperlyConfigured,
            BadOffSchedule1.objects.create,
            subject_identifier=self.subject_identifier,
            my_offschedule_date=get_utcnow(),
        )

    def test_offschedule_no_meta_defaults_offschedule_field(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule7)

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
        )
        OnScheduleSeven.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=2),
        )

        offschedule_datetime = get_utcnow()
        obj = OffScheduleSeven.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=offschedule_datetime,
        )

        self.assertEqual(obj.offschedule_datetime, offschedule_datetime)

    def test_onschedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OnSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )

    def test_offschedule_raises(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        self.assertRaises(
            RegistryNotLoaded,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )

    def test_on_offschedule(self):
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=3),
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=3),
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, ON_SCHEDULE)
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(history_obj.schedule_status, OFF_SCHEDULE)

    def test_history(self):
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=3),
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=3),
        )
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
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

    def test_crf(self):
        """Assert can enter a CRF.
        """
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=3),
        )
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=3),
        )
        appointments = Appointment.objects.all()
        self.assertEqual(appointments.count(), 4)
        appointment = Appointment.objects.all().order_by("appt_datetime").first()
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

    def test_onschedules_manager(self):
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(months=3),
        )
        onschedule_datetime = get_utcnow() - relativedelta(months=3)

        onschedule = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )

        history = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual([onschedule], [obj for obj in history])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier, report_datetime=get_utcnow()
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=onschedule_datetime - relativedelta(months=4),
        )
        self.assertEqual(0, len(onschedules))

        # add offschedule
        offschedule_datetime = onschedule_datetime + relativedelta(months=2)
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=offschedule_datetime,
        )

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=offschedule_datetime + relativedelta(days=1),
        )
        self.assertEqual(0, len(onschedules))

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=offschedule_datetime,
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])

        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=offschedule_datetime - relativedelta(months=1),
        )
        self.assertEqual([onschedule], [obj for obj in onschedules])
        onschedules = SubjectScheduleHistory.objects.onschedules(
            subject_identifier=self.subject_identifier,
            report_datetime=offschedule_datetime + relativedelta(months=1),
        )
        self.assertEqual(0, len(onschedules))

    def test_natural_key(self):
        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(months=3),
        )
        obj = OnSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
        obj = OffSchedule.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(obj.natural_key(), (self.subject_identifier,))
