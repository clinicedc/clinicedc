from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent1_v1, consent1_v2, consent2_v1, consent2_v2
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_consent.site_consents import site_consents
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.exceptions import SubjectScheduleError
from edc_visit_schedule.models import OffSchedule, OnSchedule, SubjectScheduleHistory
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.subject_schedule import SubjectSchedule
from edc_visit_schedule.visit_schedule import VisitSchedule


@tag("visit_schedule")
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=30)
class TestSubjectSchedule(SiteTestCaseMixin, TestCase):
    def setUp(self):
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime

        site_consents.registry = {}
        site_consents.register(consent1_v1)
        site_consents.register(consent1_v2)
        site_consents.register(consent2_v1, updated_by=consent2_v2)
        site_consents.register(consent2_v2)

        site_visit_schedules._registry = {}

        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.OnSchedule",
            offschedule_model="edc_visit_schedule.OffSchedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent2_v1],
            base_timepoint=1,
        )
        schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="clinicedc_tests.OnScheduleThree",
            offschedule_model="clinicedc_tests.OffScheduleThree",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent2_v2],
            base_timepoint=1,
        )
        visit_schedule1 = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_offstudy.SubjectOffstudy",
            death_report_model="clinicedc_tests.DeathReport",
        )
        visit_schedule1.add_schedule(schedule)
        visit_schedule1.add_schedule(schedule3)
        site_visit_schedules.register(visit_schedule1)

        schedule2 = Schedule(
            name="schedule_two",
            onschedule_model="clinicedc_tests.OnScheduleTwo",
            offschedule_model="clinicedc_tests.OffScheduleTwo",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent1_v1],
        )
        schedule4 = Schedule(
            name="schedule_four",
            onschedule_model="clinicedc_tests.OnScheduleFour",
            offschedule_model="clinicedc_tests.OffScheduleFour",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent1_v2],
        )
        visit_schedule2 = VisitSchedule(
            name="visit_schedule_two",
            verbose_name="Visit Schedule Two",
            offstudy_model="edc_offstudy.SubjectOffstudy",
            death_report_model="clinicedc_tests.DeathReport",
        )
        visit_schedule2.add_schedule(schedule4)
        visit_schedule2.add_schedule(schedule2)
        site_visit_schedules.register(visit_schedule2)

    def test_onschedule_updates_history(self):
        """Asserts returns the correct instances for the schedule."""
        helper = Helper()
        subject_screening, first_name, last_name = helper.screen_subject(
            report_datetime=get_utcnow()
        )
        for onschedule_model, schedule_name, cdef in [
            ("clinicedc_tests.onscheduletwo", "schedule_two", consent1_v1),
        ]:
            with self.subTest(onschedule_model=onschedule_model, schedule_name=schedule_name):
                subject_consent = helper.consent_subject(
                    consent_definition=cdef,
                    subject_screening=subject_screening,
                    first_name=first_name,
                    last_name=last_name,
                )
                visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
                    onschedule_model
                )
                subject_schedule = SubjectSchedule(
                    subject_consent.subject_identifier,
                    visit_schedule=visit_schedule,
                    schedule=schedule,
                )
                subject_schedule.put_on_schedule(
                    onschedule_datetime=get_utcnow(),
                    # consent_definition=subject_consent.consent_definition,
                )
                try:
                    SubjectScheduleHistory.objects.get(
                        subject_identifier=subject_consent.subject_identifier,
                        schedule_name=schedule_name,
                    )
                except ObjectDoesNotExist:
                    self.fail("ObjectDoesNotExist unexpectedly raised")

        traveller = time_machine.travel(get_utcnow() + relativedelta(days=52))
        traveller.start()
        for onschedule_model, schedule_name, cdef in [
            ("clinicedc_tests.onschedulefour", "schedule_four", consent1_v2),
        ]:
            with self.subTest(onschedule_model=onschedule_model, schedule_name=schedule_name):
                subject_consent = helper.consent_subject(
                    consent_definition=cdef,
                    subject_screening=subject_screening,
                    consent_datetime=get_utcnow(),
                    first_name=first_name,
                    last_name=last_name,
                )
                visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
                    onschedule_model
                )
                subject_schedule = SubjectSchedule(
                    subject_consent.subject_identifier,
                    visit_schedule=visit_schedule,
                    schedule=schedule,
                )
                subject_schedule.put_on_schedule(
                    onschedule_datetime=get_utcnow(),
                    # consent_definition=subject_consent.consent_definition,
                )
                try:
                    SubjectScheduleHistory.objects.get(
                        subject_identifier=subject_consent.subject_identifier,
                        schedule_name=schedule_name,
                    )
                except ObjectDoesNotExist:
                    self.fail("ObjectDoesNotExist unexpectedly raised")
        traveller.stop()

    def test_multpile_consents(self):
        """Asserts does not raise if more than one consent
        for this subject
        """
        helper = Helper()
        subject_screening, first_name, last_name = helper.screen_subject(
            report_datetime=get_utcnow()
        )
        helper.consent_subject(
            consent_definition=consent2_v1,
            subject_screening=subject_screening,
            first_name=first_name,
            last_name=last_name,
        )
        # updates
        traveller = time_machine.travel(get_utcnow() + relativedelta(days=52))
        traveller.start()
        subject_consent = helper.consent_subject(
            consent_definition=consent2_v2,
            subject_screening=subject_screening,
            first_name=first_name,
            last_name=last_name,
        )

        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
            "clinicedc_tests.OnScheduleThree"
        )
        subject_schedule = SubjectSchedule(
            subject_consent.subject_identifier,
            visit_schedule=visit_schedule,
            schedule=schedule,
        )
        try:
            subject_schedule.put_on_schedule(
                onschedule_datetime=get_utcnow(),
                # consent_definition=subject_consent.consent_definition,
            )
        except SubjectScheduleError:
            self.fail("SubjectScheduleError unexpectedly raised.")
        traveller.stop()

    def test_resave(self):
        """Asserts returns the correct instances for the schedule."""
        helper = Helper()
        subject_screening, first_name, last_name = helper.screen_subject(
            report_datetime=get_utcnow()
        )
        subject_consent = helper.consent_subject(
            consent_definition=consent2_v1,
            subject_screening=subject_screening,
            first_name=first_name,
            last_name=last_name,
        )
        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        subject_schedule = SubjectSchedule(
            subject_consent.subject_identifier,
            visit_schedule=visit_schedule,
            schedule=schedule,
        )
        onschedule_datetime: datetime = get_utcnow()
        subject_schedule.put_on_schedule(onschedule_datetime)
        subject_schedule.put_on_schedule(onschedule_datetime)

    def test_put_on_schedule(self):
        helper = Helper()
        subject_screening, first_name, last_name = helper.screen_subject(
            report_datetime=get_utcnow()
        )
        subject_consent = helper.consent_subject(
            consent_definition=consent2_v1,
            subject_screening=subject_screening,
            first_name=first_name,
            last_name=last_name,
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.assertRaises(
            ObjectDoesNotExist,
            OnSchedule.objects.get,
            subject_identifier=subject_consent.subject_identifier,
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=get_utcnow(),
            # consent_definition=subject_consent.consent_definition,
        )
        try:
            OnSchedule.objects.get(subject_identifier=subject_consent.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_take_off_schedule(self):
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent2_v1,
        )
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name="visit_schedule"
        )
        schedule = visit_schedule.schedules.get("schedule")
        traveller = time_machine.travel(get_utcnow() + relativedelta(hours=+2))
        traveller.start()
        schedule.put_on_schedule(
            subject_consent.subject_identifier,
            get_utcnow(),
            # consent_definition=subject_consent.consent_definition,
        )
        traveller.stop()
        traveller = time_machine.travel(get_utcnow() + relativedelta(months=+1))
        traveller.start()
        schedule.take_off_schedule(subject_consent.subject_identifier, get_utcnow())
        try:
            OffSchedule.objects.get(subject_identifier=subject_consent.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
        traveller.stop()
