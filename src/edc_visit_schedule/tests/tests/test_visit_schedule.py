from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings, tag

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.utils import check_visit_schedule_models
from edc_visit_schedule.visit_schedule import VisitSchedule, VisitScheduleNameError
from tests.sites import all_sites


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=10)
class TestVisitSchedule(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        super().setUp()
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

    def test_visit_schedule_name(self):
        """Asserts raises on invalid name."""
        self.assertRaises(
            VisitScheduleNameError,
            VisitSchedule,
            name="visit &&&& schedule",
            verbose_name="Visit Schedule",
            offstudy_model="tests.deathreport",
            death_report_model="tests.deathreport",
            locator_model="edc_locator.subjectlocator",
        )

    def test_visit_schedule_repr(self):
        """Asserts repr evaluates correctly."""
        v = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="tests.deathreport",
            death_report_model="tests.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        self.assertTrue(v.__repr__())

    def test_visit_schedule_validates(self):
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_offstudy.subjectoffstudy",
            death_report_model="tests.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        errors = check_visit_schedule_models(visit_schedule)
        if errors:
            self.fail("visit_schedule.check() unexpectedly failed")
