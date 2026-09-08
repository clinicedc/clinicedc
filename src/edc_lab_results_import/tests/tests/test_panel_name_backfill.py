from __future__ import annotations

import io
from decimal import Decimal

from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.management import call_command
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_lab_panel.panels import wbc_differential
from edc_lab_results_import.backfill import PanelNameBackfill
from edc_lab_results_import.models import Result
from edc_lab_results_import.utils import get_panel_name_by_utestid
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results_import")
@override_settings(SITE_ID=10)
class TestPanelNameBackfill(TestCase):
    """`prepare_imported_result` resolved `panel_name` into the
    dataframe and did not persist it, so every result imported before
    that fix carries an empty panel and nothing that joins on panel
    works.
    """

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )

    def create_result(self, utestid: str, panel_name: str = "") -> Result:
        return Result.objects.create(
            subject_identifier=self.subject_visit.subject_identifier,
            subject_visit=self.subject_visit,
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name=panel_name,
            source_file="report_001.pdf",
            utestid=utestid,
            source_utestid=utestid.upper(),
            result_value=Decimal("13.4"),
            units=GRAMS_PER_DECILITER,
            result_no=f"RES-{utestid}",
            order_no="ORD001",
            sample_no="SAM001",
            result_status="final",
            name_id="NAME001",
            result_datetime=timezone.now(),
        )

    @staticmethod
    def backfill(**kwargs):
        return PanelNameBackfill(stdout=io.StringIO(), **kwargs).run()

    def test_sets_the_panel_from_the_utestid(self):
        result = self.create_result("haemoglobin")
        summary = self.backfill()
        self.assertEqual(1, summary.candidates)
        self.assertEqual(1, summary.updated)
        result.refresh_from_db()
        self.assertEqual("fbc", result.panel_name)

    def test_leaves_a_result_that_already_has_a_panel(self):
        self.create_result("haemoglobin", panel_name="fbc")
        summary = self.backfill()
        self.assertEqual(0, summary.candidates)

    def test_counts_a_utestid_in_no_panel_and_leaves_it_empty(self):
        """Inventing a panel would be worse than leaving it visible as
        `panel_unknown` in `get_df_orphan_results`.
        """
        result = self.create_result("not_a_real_utestid")
        summary = self.backfill()
        self.assertEqual(1, summary.unmapped)
        self.assertEqual(0, summary.updated)
        result.refresh_from_db()
        self.assertEqual("", result.panel_name)

    def test_covers_the_differential_analytes(self):
        """These are reported under their own panel, which no lab
        profile registers because they are drawn under FBC.
        """
        result = self.create_result("mono_abs")
        self.backfill()
        result.refresh_from_db()
        self.assertEqual(wbc_differential.name, result.panel_name)

    def test_without_the_differential_panel_they_stay_empty(self):
        """What `import_results` did before it passed `extra_panels`."""
        result = self.create_result("mono_abs")
        summary = self.backfill(extra_panels=[])
        self.assertEqual(1, summary.unmapped)
        result.refresh_from_db()
        self.assertEqual("", result.panel_name)

    def test_a_dry_run_writes_nothing(self):
        result = self.create_result("haemoglobin")
        summary = self.backfill(dry_run=True)
        self.assertEqual(1, summary.updated)
        result.refresh_from_db()
        self.assertEqual("", result.panel_name)

    def test_the_change_is_recorded_in_the_history(self):
        result = self.create_result("haemoglobin")
        before = result.history.count()
        self.backfill()
        self.assertEqual(before + 1, result.history.count())
        self.assertEqual("fbc", result.history.first().panel_name)

    def test_management_command_runs(self):
        result = self.create_result("haemoglobin")
        call_command("backfill_panel_name", stdout=io.StringIO())
        result.refresh_from_db()
        self.assertEqual("fbc", result.panel_name)


@tag("lab_results_import")
class TestPanelNameByUtestid(TestCase):
    def test_maps_a_registered_utestid_to_its_panel(self):
        self.assertEqual("fbc", get_panel_name_by_utestid().get("haemoglobin"))

    def test_the_differential_analytes_need_the_extra_panel(self):
        """No lab profile registers `wbc_differential`, so without it
        every differential utest id resolves to no panel and the result
        can never be matched to a requisition.
        """
        self.assertIsNone(get_panel_name_by_utestid().get("mono_abs"))
        mapping = get_panel_name_by_utestid([wbc_differential])
        for utest_id in wbc_differential.flatten_utestids():
            self.assertEqual(wbc_differential.name, mapping.get(utest_id), utest_id)

    def test_passing_an_already_registered_panel_is_harmless(self):
        """`import_results` passes the differential panel whether or not
        a deployment also registers it.
        """
        mapping = get_panel_name_by_utestid([wbc_differential, wbc_differential])
        self.assertEqual(wbc_differential.name, mapping.get("mono_abs"))
