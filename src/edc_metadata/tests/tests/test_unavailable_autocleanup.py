from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfFour
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase, override_settings, tag

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.models import CrfMetadataMissing, DataMissingReason
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestUnavailableAutoCleanup(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
            Panel.objects.create(name=name)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name, schedule_name="schedule"
        )
        self.appointment = self.subject_visit.appointment
        self.sid = self.subject_visit.subject_identifier
        self.reason = DataMissingReason.objects.create(
            name="test_reason", display_name="Test reason"
        )

    def _opts(self, model: str) -> dict:
        return dict(
            subject_identifier=self.sid,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=0,
            model=model,
        )

    def test_keying_a_crf_deletes_its_unavailable_flag(self):
        # flag the (yet-unkeyed) CrfFour at baseline as data unavailable
        opts = self._opts(CrfFour._meta.label_lower)
        CrfMetadataMissing.objects.create(**opts, reason=self.reason, site_id=10)
        self.assertTrue(CrfMetadataMissing.objects.filter(**opts).exists())

        # keying the CRF (saving the source model) fires the cleanup signal
        CrfFour.objects.create(subject_visit=self.subject_visit)
        self.assertFalse(CrfMetadataMissing.objects.filter(**opts).exists())

    def test_unrelated_flag_is_left_alone(self):
        # a flag for a different form is not touched when CrfFour is keyed
        opts = self._opts("clinicedc_tests.crffive")
        CrfMetadataMissing.objects.create(**opts, reason=self.reason, site_id=10)
        CrfFour.objects.create(subject_visit=self.subject_visit)
        self.assertTrue(CrfMetadataMissing.objects.filter(**opts).exists())
