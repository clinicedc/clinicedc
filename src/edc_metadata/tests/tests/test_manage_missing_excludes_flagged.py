from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

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
from edc_metadata.views.manage_missing import visit_columns
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

    def test_flagged_ids_scoped_to_other_visit_code_misses_the_flag(self):
        """Documents the trap: a visit_code-scoped base misses flags at other
        visits, which is why the all-visits overview must not scope by it."""
        flagged_crf = self._flag_one()
        other_base = ManageMissingView.base_filter(
            [10], self.vsn, self.sn, "not_the_flagged_visit", None
        )
        # scoped to a different visit_code -> the flag is not resolved
        self.assertEqual(
            ManageMissingView._flagged_ids(CrfMetadata, CrfMetadataMissing, other_base),
            set(),
        )
        # dropping visit_code (as the overview lens now does) resolves it again
        unscoped = {k: v for k, v in other_base.items() if k != "visit_code"}
        flagged = ManageMissingView._flagged_ids(CrfMetadata, CrfMetadataMissing, unscoped)
        self.assertEqual(flagged, {flagged_crf.id})

    def test_overview_hides_flagged_despite_differing_visit_code_filter(self):
        """Regression: with a visit_code filter that differs from the flag's
        visit, the flagged CRF must still drop out of the overview totals."""
        flagged_crf = self._flag_one()
        model_label = flagged_crf.model
        columns = visit_columns(self.vsn, self.sn)
        visit_index = [code for code, _ in columns].index(self.baseline)

        view = ManageMissingView()
        # empty `site` param -> selected_site_value() returns "" without needing
        # request.site, which RequestFactory does not populate.
        view.request = RequestFactory().get("/review/?site=")

        def _cell_count(exclude_ids):
            overview = view.overview(
                [10], self.vsn, self.sn, [model_label], columns, exclude_ids=exclude_ids
            )
            row = next((r for r in overview if r["model"] == model_label), None)
            return 0 if row is None else row["cells"][visit_index]["count"]

        # buggy scope (visit_code carried into the exclude) leaves it visible ...
        scoped_base = ManageMissingView.base_filter(
            [10], self.vsn, self.sn, "not_the_flagged_visit", None
        )
        scoped_exclude = ManageMissingView._flagged_ids(
            CrfMetadata, CrfMetadataMissing, scoped_base
        )
        self.assertEqual(_cell_count(scoped_exclude), 1)

        # ... the fixed scope (no visit_code) hides it
        unscoped = {k: v for k, v in scoped_base.items() if k != "visit_code"}
        fixed_exclude = ManageMissingView._flagged_ids(
            CrfMetadata, CrfMetadataMissing, unscoped
        )
        self.assertEqual(_cell_count(fixed_exclude), 0)
