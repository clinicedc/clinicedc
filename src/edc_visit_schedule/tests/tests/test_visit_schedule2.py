from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.sites import all_sites
from django.test import TestCase, override_settings, tag

from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, FormsCollectionError
from edc_visit_schedule.visit_schedule import AlreadyRegisteredSchedule, VisitSchedule


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=10)
class TestVisitSchedule2(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)

        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_offstudy.subjectoffstudy",
            death_report_model="clinicedc_tests.deathreport",
            locator_model="edc_locator.subjectlocator",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
        )

        self.schedule2 = Schedule(
            name="schedule_two",
            onschedule_model="clinicedc_tests.onscheduletwo",
            offschedule_model="clinicedc_tests.offscheduletwo",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
        )

        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="clinicedc_tests.onschedulethree",
            offschedule_model="clinicedc_tests.offschedulethree",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
        )

    def test_visit_schedule_add_schedule(self):
        try:
            self.visit_schedule.add_schedule(self.schedule)
        except AlreadyRegisteredSchedule:
            self.fail("AlreadyRegisteredSchedule unexpectedly raised.")

    def test_visit_schedule_add_schedule_with_appointment_model(self):
        self.visit_schedule.add_schedule(self.schedule3)
        for schedule in self.visit_schedule.schedules.values():
            self.assertEqual(schedule.appointment_model, "edc_appointment.appointment")

    def test_visit_already_added_to_schedule(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.assertRaises(
            AlreadyRegisteredSchedule, self.visit_schedule.add_schedule, self.schedule
        )

    def test_visit_schedule_get_schedules(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.assertIn(self.schedule, self.visit_schedule.schedules.values())
        self.visit_schedule.add_schedule(self.schedule3)
        self.assertIn(self.schedule3, self.visit_schedule.schedules.values())

    def test_crfs_unique_show_order(self):
        self.assertRaises(
            FormsCollectionError,
            FormsCollection,
            Crf(show_order=10, model="edc_example.CrfOne"),
            Crf(show_order=20, model="edc_example.CrfTwo"),
            Crf(show_order=20, model="edc_example.CrfThree"),
        )
