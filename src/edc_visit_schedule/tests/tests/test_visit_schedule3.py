from datetime import date, datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import NotConsentedError
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_registration.models import RegisteredSubject
from edc_registration.utils import RegisteredSubjectDoesNotExist
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.constants import ON_SCHEDULE
from edc_visit_schedule.exceptions import (
    InvalidOffscheduleDate,
    NotOnScheduleError,
    SiteVisitScheduleError,
)
from edc_visit_schedule.models import (
    OffSchedule,
    OnSchedule,
    SubjectScheduleHistory,
    VisitSchedule,
)
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Visit
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from tests.models import OnScheduleThree, SubjectConsent


@time_machine.travel(datetime(2025, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
class TestVisitSchedule3(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        self.consent_v1 = ConsentDefinition(
            "tests.subjectconsentv1",
            version="1",
            start=self.study_open_datetime,
            end=self.study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.registry = {}
        site_consents.register(self.consent_v1)
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="tests.subjectoffstudy",
            death_report_model="tests.deathreport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[self.consent_v1],
            base_timepoint=1,
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            timepoint=1,
        )
        self.schedule.add_visit(visit)
        self.visit_schedule.add_schedule(self.schedule)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        site_consents.registry = {}
        for cdef in self.schedule.consent_definitions:
            site_consents.register(cdef)
        cdef = self.schedule.consent_definitions[0]
        self.subject_consent = cdef.model_create(
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime,
            dob=date(1995, 1, 1),
            identity="11111",
            confirm_identity="11111",
            version=cdef.version,
        )
        self.subject_identifier = self.subject_consent.subject_identifier

    def test_put_on_schedule_creates_history(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertEqual(
            SubjectScheduleHistory.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )
        traveller.stop()

    def test_onschedule_creates_history(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()

        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertEqual(
            SubjectScheduleHistory.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertIsNone(history_obj.__dict__.get("offschedule_datetime"))

        onschedule_model_obj = OnSchedule.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(
            history_obj.__dict__.get("onschedule_datetime"),
            onschedule_model_obj.onschedule_datetime,
        )
        self.assertEqual(history_obj.__dict__.get("schedule_status"), ON_SCHEDULE)
        traveller.stop()

    def test_can_create_offschedule_with_onschedule(self):
        # signal puts on schedule
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        try:
            OffSchedule.objects.create(
                subject_identifier=self.subject_identifier,
                offschedule_datetime=get_utcnow(),
            )
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}.")
        traveller.stop()

    def test_creates_appointments(self):
        # signal puts on schedule
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        onschedule_datetime = get_utcnow()
        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        self.assertGreater(Appointment.objects.all().count(), 0)
        traveller.stop()

    def test_creates_appointments_starting_with_onschedule_datetime(self):
        """Will pass as long as this is not a holiday"""
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        onschedule_datetime = self.subject_consent.consent_datetime + relativedelta(
            days=28
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        appointment = Appointment.objects.all().order_by("appt_datetime").first()
        self.assertEqual(appointment.appt_datetime, onschedule_datetime)
        traveller.stop()

    def test_cannot_create_offschedule_without_onschedule(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.assertEqual(
            OnSchedule.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            0,
        )
        self.assertRaises(
            NotOnScheduleError,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )
        traveller.stop()

    def test_cannot_create_offschedule_before_onschedule(self):
        traveller = time_machine.travel(
            self.study_open_datetime + relativedelta(days=28)
        )
        traveller.start()
        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertRaises(
            InvalidOffscheduleDate,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow() - relativedelta(days=1),
        )
        traveller.stop()

    def test_cannot_create_offschedule_before_last_visit(self):
        traveller = time_machine.travel(
            self.study_open_datetime + relativedelta(days=10)
        )
        traveller.start()
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )
        appointments = Appointment.objects.all()
        traveller.stop()

        traveller = time_machine.travel(appointments[0].appt_datetime)
        traveller.start()
        SubjectVisit.objects.create(
            appointment=appointments[0],
            subject_identifier=self.subject_identifier,
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        self.assertRaises(
            InvalidOffscheduleDate,
            schedule.take_off_schedule,
            subject_identifier=self.subject_identifier,
            offschedule_datetime=appointments[0].appt_datetime - relativedelta(days=1),
        )
        traveller.stop()

    def test_cannot_put_on_schedule_if_visit_schedule_not_registered_subject(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        onschedule_datetime = self.subject_consent.consent_datetime + relativedelta(
            days=10
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        RegisteredSubject.objects.all().delete()
        self.assertRaises(
            RegisteredSubjectDoesNotExist,
            schedule.put_on_schedule,
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        traveller.stop()

    def test_cannot_put_on_schedule_if_visit_schedule_not_consented(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        onschedule_datetime = self.subject_consent.consent_datetime + relativedelta(
            days=10
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        SubjectConsent.objects.all().delete()
        self.assertRaises(
            NotConsentedError,
            schedule.put_on_schedule,
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        traveller.stop()

    def test_cannot_put_on_schedule_if_schedule_not_added(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.assertRaises(
            SiteVisitScheduleError,
            OnScheduleThree.objects.put_on_schedule,
            self.subject_identifier,
        )
        traveller.stop()
