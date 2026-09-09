from __future__ import annotations

import io
from decimal import Decimal

import pandas as pd
from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER, YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_panel.panels import wbc_differential
from edc_lab_results_import.constants import PANEL_NOT_EXPECTED, RESOLVER_MISS
from edc_lab_results_import.dataframes import get_df_orphan_results
from edc_lab_results_import.models import Result
from edc_lab_results_import.result_linker import ResultLinker
from edc_lab_results_import.utils import get_requisition_panel_name_map
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

PANEL_MAP = {wbc_differential.name: "fbc"}


@tag("lab_results_import")
@override_settings(SITE_ID=10)
class TestRequisitionPanelMap(TestCase):
    """The panel a result is reported under is not always the panel it
    was drawn under.

    The white cell differentials are their own analyte panel, but no
    visit schedule requires a `wbc_diff` requisition because they are
    collected on the FBC requisition. Looking one up by the analyte
    panel can only fail, which in meta was 56,544 results.
    """

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier

    def create_fbc_requisition(self) -> SubjectRequisition:
        return SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name="fbc"),
            requisition_datetime=self.subject_visit.report_datetime,
            is_drawn=YES,
            drawn_datetime=self.subject_visit.report_datetime,
        )

    def create_differential_result(self) -> Result:
        """An imported differential carrying its analyte panel."""
        return Result.objects.create(
            subject_identifier=self.subject_identifier,
            subject_visit=None,
            requisition=None,
            requisition_identifier="",
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name=wbc_differential.name,
            source_file="report_001.pdf",
            utestid="mono_abs",
            source_utestid="MONO_ABS",
            result_value=Decimal("0.5"),
            units=GRAMS_PER_DECILITER,
            result_no="RES-mono_abs",
            order_no="ORD001",
            sample_no="SAM001",
            result_status="final",
            name_id="NAME001",
            result_datetime=timezone.now(),
            specimen_collected_datetime=self.subject_visit.report_datetime,
        )

    def test_the_map_is_empty_by_default(self):
        self.assertEqual({}, get_requisition_panel_name_map())

    @override_settings(EDC_LAB_RESULTS_REQUISITION_PANEL_MAP=PANEL_MAP)
    def test_the_map_is_read_from_settings(self):
        self.assertEqual(PANEL_MAP, get_requisition_panel_name_map())

    def test_without_the_map_a_differential_finds_no_requisition(self):
        """No `wbc_diff` requisition exists, so the lookup can only
        fail.
        """
        self.create_fbc_requisition()
        self.create_differential_result()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(PANEL_NOT_EXPECTED, row["bucket"])
        self.assertTrue(pd.isna(row["requisition_id"]))

    @override_settings(EDC_LAB_RESULTS_REQUISITION_PANEL_MAP=PANEL_MAP)
    def test_with_the_map_a_differential_finds_the_fbc_requisition(self):
        requisition = self.create_fbc_requisition()
        self.create_differential_result()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(RESOLVER_MISS, row["bucket"])
        self.assertEqual(str(requisition.id), row["requisition_id"])

    @override_settings(EDC_LAB_RESULTS_REQUISITION_PANEL_MAP=PANEL_MAP)
    def test_the_analyte_panel_is_kept(self):
        """`Result.panel_name` stays the truthful description of what
        was measured. Only the lookup uses the requisition panel.
        """
        self.create_fbc_requisition()
        result = self.create_differential_result()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(wbc_differential.name, row["panel_name"])
        self.assertEqual("fbc", row["requisition_panel_name"])
        result.refresh_from_db()
        self.assertEqual(wbc_differential.name, result.panel_name)

    @override_settings(EDC_LAB_RESULTS_REQUISITION_PANEL_MAP=PANEL_MAP)
    def test_an_unlisted_panel_maps_to_itself(self):
        self.create_fbc_requisition()
        result = self.create_differential_result()
        Result.objects.filter(id=result.id).update(panel_name="fbc", utestid="haemoglobin")
        row = get_df_orphan_results().iloc[0]
        self.assertEqual("fbc", row["panel_name"])
        self.assertEqual("fbc", row["requisition_panel_name"])

    @override_settings(EDC_LAB_RESULTS_REQUISITION_PANEL_MAP=PANEL_MAP)
    def test_the_linker_can_then_link_a_differential(self):
        """The payoff: these become linkable without anyone keying
        anything.
        """
        requisition = self.create_fbc_requisition()
        result = self.create_differential_result()
        summary = ResultLinker(stdout=io.StringIO()).run()
        self.assertEqual(1, summary.linked)
        result.refresh_from_db()
        self.assertEqual(requisition.id, result.requisition_id)
        self.assertEqual(wbc_differential.name, result.panel_name)
