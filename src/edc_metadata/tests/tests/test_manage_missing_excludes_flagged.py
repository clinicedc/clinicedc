from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase, override_settings, tag

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.constants import REQUIRED
from edc_metadata.models import (
    CrfMetadata,
    CrfMetadataMissing,
    DataMissingReason,
)
from edc_metadata.views import ManageMissingView
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestManageMissingExcludesFlagged(TestCase):
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
        self.vsn = self.appointment.visit_schedule_name
        self.sn = self.appointment.schedule_name
        self.baseline = self.appointment.visit_code
        self.reason = DataMissingReason.objects.create(
            name="test_reason", display_name="Test reason"
        )
        self.base = ManageMissingView.base_filter([10], self.vsn, self.sn, None, None)

    def _flag_one(self):
        crf = CrfMetadata.objects.filter(
            entry_status=REQUIRED, site_id=10, subject_identifier=self.sid
        ).first()
        CrfMetadataMissing.objects.create(
            subject_identifier=crf.subject_identifier,
            visit_schedule_name=crf.visit_schedule_name,
            schedule_name=crf.schedule_name,
            visit_code=crf.visit_code,
            visit_code_sequence=crf.visit_code_sequence,
            model=crf.model,
            reason=self.reason,
            site_id=10,
        )
        return crf

    def test_flagged_ids_resolves_the_flag(self):
        self._flag_one()
        flagged = ManageMissingView._flagged_ids(CrfMetadata, CrfMetadataMissing, self.base)
        self.assertEqual(len(flagged), 1)

    def test_counts_drop_by_one_when_flagged(self):
        before = ManageMissingView._subject_totals(CrfMetadata, self.base)[self.sid]
        self._flag_one()
        flagged = ManageMissingView._flagged_ids(CrfMetadata, CrfMetadataMissing, self.base)
        after = ManageMissingView._subject_totals(CrfMetadata, self.base, flagged)[self.sid]
        self.assertEqual(after, before - 1)

        cells_before = ManageMissingView._cell_counts(CrfMetadata, self.base, [self.sid])[
            (self.sid, self.baseline)
        ]
        cells_after = ManageMissingView._cell_counts(
            CrfMetadata, self.base, [self.sid], flagged
        )[(self.sid, self.baseline)]
        self.assertEqual(cells_after, cells_before - 1)

        cols_before = ManageMissingView._column_counts(CrfMetadata, self.base)[self.baseline]
        cols_after = ManageMissingView._column_counts(CrfMetadata, self.base, flagged)[
            self.baseline
        ]
        self.assertEqual(cols_after, cols_before - 1)
