from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectConsentV1Ext
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule_consent.visit_schedule import (
    get_visit_schedule,
)
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition_extension import ConsentDefinitionExtension
from edc_consent.tests.consent_test_utils import consent_factory
from edc_constants.constants import NO, YES
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("consent")
@time_machine.travel(datetime(2025, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(EDC_AUTH_SKIP_SITE_AUTHS=True, EDC_AUTH_SKIP_AUTH_UPDATER=False, SITE_ID=10)
class TestConsentExtension(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}
        self.consent_v1 = consent_factory(
            proxy_model="clinicedc_tests.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_v1_ext = ConsentDefinitionExtension(
            "clinicedc_tests.subjectconsentv1ext",
            version="1.1",
            start=self.study_open_datetime,
            extends=self.consent_v1,
            timepoints=[3, 4],
        )
        site_consents.register(self.consent_v1, extended_by=consent_v1_ext)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule([self.consent_v1], extend=True))

        self.dob = self.study_open_datetime - relativedelta(years=25)

    def test_consent_version_extension(self):
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=self.consent_v1,
            report_datetime=self.study_open_datetime + timedelta(days=1),
        )
        self.assertEqual(subject_consent.version, "1.0")
        self.assertEqual(Appointment.objects.all().count(), 3)

        consent_ext = SubjectConsentV1Ext.objects.create(
            subject_consent=subject_consent,
            report_datetime=subject_consent.consent_datetime + timedelta(days=1),
            agrees_to_extension=YES,
        )
        self.assertEqual(Appointment.objects.all().count(), 5)
        consent_ext.agrees_to_extension = NO
        consent_ext.save()
        self.assertEqual(Appointment.objects.all().count(), 3)
