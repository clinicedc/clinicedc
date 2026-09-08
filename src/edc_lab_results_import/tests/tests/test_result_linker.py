from __future__ import annotations

import io
from decimal import Decimal

import pandas as pd
from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER, NO, YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.management import call_command
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results_import.dataframes import (
    changed_since_pulled,
    get_df_orphan_results,
    get_pulled_datetime,
    results_changed_since,
)
from edc_lab_results_import.models import Result
from edc_lab_results_import.result_linker import ResultLinker
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results_import")
@override_settings(SITE_ID=10)
class TestResultLinker(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier

    def create_requisition(self, panel_name: str = "fbc", **kwargs) -> SubjectRequisition:
        opts = dict(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name=panel_name),
            requisition_datetime=self.subject_visit.report_datetime,
        )
        opts.update(**kwargs)
        return SubjectRequisition.objects.create(**opts)

    def create_orphan(self, utestid: str = "haemoglobin", **kwargs) -> Result:
        opts = dict(
            subject_identifier=self.subject_identifier,
            screening_identifier="SCR0001",
            subject_visit=None,
            requisition=None,
            requisition_identifier="",
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name="fbc",
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
            specimen_collected_datetime=self.subject_visit.report_datetime,
        )
        opts.update(**kwargs)
        return Result.objects.create(**opts)

    @staticmethod
    def link(**kwargs):
        return ResultLinker(stdout=io.StringIO(), **kwargs).run()

    def test_links_the_result_to_the_requisition_that_already_exists(self):
        requisition = self.create_requisition()
        result = self.create_orphan()
        summary = self.link()
        self.assertEqual(1, summary.candidates)
        self.assertEqual(1, summary.linked)
        result.refresh_from_db()
        self.assertEqual(requisition.id, result.requisition_id)
        self.assertEqual(requisition.requisition_identifier, result.requisition_identifier)
        self.assertEqual(requisition.requisition_datetime, result.requisition_datetime)

    def test_links_the_related_visit_too(self):
        """`ResultSearchView.get_crf_buttons` needs both, so a result
        linked to a requisition but not to a visit is still unusable.
        """
        self.create_requisition()
        result = self.create_orphan()
        self.link()
        result.refresh_from_db()
        self.assertEqual(self.subject_visit.id, result.subject_visit_id)

    def test_result_carries_no_historical_model(self):
        """Pins a fact the linker depends on being told about.

        `BaseUuidModel` does not add `HistoricalRecords`, models opt in,
        and `Result` does not. So linking leaves no audit trail beyond
        `modified`. If `Result` is ever given a history, revisit
        `ResultLinker`, which saves one row at a time for a trail that
        does not yet exist.
        """
        self.assertFalse(hasattr(Result, "history"))

    def test_the_link_moves_modified_so_staleness_can_see_it(self):
        self.create_requisition()
        result = self.create_orphan()
        pulled = timezone.now()
        self.link()
        result.refresh_from_db()
        self.assertGreaterEqual(result.modified, pulled)
        self.assertEqual(1, results_changed_since(pulled)["results_modified"])

    def test_a_dry_run_writes_nothing(self):
        self.create_requisition()
        result = self.create_orphan()
        summary = self.link(dry_run=True)
        self.assertEqual(1, summary.linked)
        result.refresh_from_db()
        self.assertIsNone(result.requisition_id)

    def test_nothing_to_link_where_no_requisition_exists(self):
        self.create_orphan()
        summary = self.link()
        self.assertEqual(0, summary.candidates)
        self.assertEqual(0, summary.linked)

    def test_a_result_already_linked_is_left_alone(self):
        """The frame is read before the write, so a result linked in
        between must not be relinked.
        """
        requisition = self.create_requisition()
        result = self.create_orphan()
        linker = ResultLinker(stdout=io.StringIO())
        df = linker.get_df()
        Result.objects.filter(id=result.id).update(requisition=requisition)
        summary = self.link()
        self.assertEqual(1, len(df))
        self.assertEqual(0, summary.linked)

    def test_counts_a_conflict_with_the_requisition(self):
        """The requisition says no result was ever coming, yet here is
        one from the lab.
        """
        self.create_requisition(
            result_expected=NO, result_not_expected_reason="30", is_drawn=YES
        )
        self.create_orphan()
        summary = self.link()
        self.assertEqual(1, summary.conflicts)
        self.assertEqual(1, summary.linked)

    def test_limits_to_one_subject(self):
        self.create_requisition()
        self.create_orphan()
        summary = self.link(subject_identifier="999-99-9999-9")
        self.assertEqual(0, summary.candidates)

    def test_batches(self):
        self.create_requisition()
        for utestid in ["haemoglobin", "wbc", "platelets"]:
            self.create_orphan(utestid=utestid)
        summary = self.link(batch_size=2)
        self.assertEqual(3, summary.linked)

    def test_management_command_runs(self):
        self.create_requisition()
        result = self.create_orphan()
        call_command("link_orphan_results", stdout=io.StringIO())
        result.refresh_from_db()
        self.assertIsNotNone(result.requisition_id)


@tag("lab_results_import")
@override_settings(SITE_ID=10)
class TestStaleness(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )

    def test_the_frame_says_when_it_was_read(self):
        before = timezone.now()
        df = get_df_orphan_results()
        self.assertIsNotNone(get_pulled_datetime(df))
        self.assertGreaterEqual(get_pulled_datetime(df), before)

    def test_nothing_changed_since_the_frame_was_read(self):
        df = get_df_orphan_results()
        self.assertEqual(
            {
                "requisitions_modified": 0,
                "requisitions_not_expecting_a_result": 0,
                "results_imported": 0,
                "results_modified": 0,
            },
            changed_since_pulled(df),
        )

    def test_a_requisition_edited_since_makes_the_frame_stale(self):
        df = get_df_orphan_results()
        SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name="fbc"),
            requisition_datetime=self.subject_visit.report_datetime,
            is_drawn=YES,
            drawn_datetime=self.subject_visit.report_datetime,
            result_expected=NO,
            result_not_expected_reason="30",
        )
        changed = changed_since_pulled(df)
        self.assertEqual(1, changed["requisitions_modified"])
        self.assertEqual(1, changed["requisitions_not_expecting_a_result"])

    def test_a_frame_with_no_timestamp_reports_nothing(self):
        self.assertEqual({}, changed_since_pulled(pd.DataFrame()))
