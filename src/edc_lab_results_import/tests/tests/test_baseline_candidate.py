from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pandas as pd
from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER, YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone
from multisite import SiteID

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results_import.constants import MAX_DAYS_BEFORE_BASELINE, VISIT_NOT_FOUND
from edc_lab_results_import.dataframes import get_df_orphan_results
from edc_lab_results_import.dataframes.get_df_orphan_results import ON_OR_BEFORE_BASELINE
from edc_lab_results_import.models import Result
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results_import")
@override_settings(SITE_ID=SiteID(10))
class TestBaselineCandidate(TestCase):
    """A specimen collected on or before a subject's first visit cannot
    belong to a later timepoint, so baseline is the only candidate.
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
        self.baseline_datetime = self.subject_visit.report_datetime

    def create_requisition(self) -> SubjectRequisition:
        return SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name="fbc"),
            requisition_datetime=self.baseline_datetime,
            is_drawn=YES,
            drawn_datetime=self.baseline_datetime,
        )

    def create_orphan(self, specimen_collected_datetime, **kwargs) -> Result:
        """A result the importer never tied to a timepoint."""
        opts = dict(
            subject_identifier=self.subject_identifier,
            subject_visit=None,
            requisition=None,
            requisition_identifier="",
            visit_code="",
            visit_code_sequence=None,
            panel_name="fbc",
            source_file="report_001.pdf",
            utestid="haemoglobin",
            source_utestid="HAEMOGLOBIN",
            result_value=Decimal("13.4"),
            units=GRAMS_PER_DECILITER,
            result_no="RES-haemoglobin",
            order_no="ORD001",
            sample_no="SAM001",
            result_status="final",
            name_id="NAME001",
            result_datetime=timezone.now(),
            specimen_collected_datetime=specimen_collected_datetime,
        )
        opts.update(**kwargs)
        return Result.objects.create(**opts)

    @staticmethod
    def get_row(df):
        return df.iloc[0]

    def test_a_specimen_drawn_before_baseline_is_proposed_for_baseline(self):
        """The screening draw captured at baseline."""
        self.create_orphan(self.baseline_datetime - timedelta(days=3))
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(VISIT_NOT_FOUND, row["bucket"])
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])
        self.assertEqual(str(self.subject_visit.id), row["candidate_subject_visit_id"])
        self.assertEqual(self.subject_visit.visit_code, row["candidate_visit_code"])
        self.assertEqual(3, row["days_before_baseline"])

    def test_a_specimen_drawn_at_baseline_is_proposed(self):
        """On or before, so the boundary is included."""
        self.create_orphan(self.baseline_datetime)
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])
        self.assertEqual(0, row["days_before_baseline"])

    def test_a_specimen_at_the_bound_is_proposed(self):
        self.create_orphan(self.baseline_datetime - timedelta(days=MAX_DAYS_BEFORE_BASELINE))
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])

    def test_a_specimen_beyond_the_bound_is_not_proposed(self):
        """`on or before` alone would claim a specimen drawn a year
        earlier.
        """
        self.create_orphan(
            self.baseline_datetime - timedelta(days=MAX_DAYS_BEFORE_BASELINE + 1)
        )
        row = self.get_row(get_df_orphan_results())
        self.assertTrue(pd.isna(row["candidate_rule"]))

    def test_the_bound_is_configurable(self):
        self.create_orphan(self.baseline_datetime - timedelta(days=60))
        self.assertTrue(pd.isna(self.get_row(get_df_orphan_results())["candidate_rule"]))
        row = self.get_row(get_df_orphan_results(max_days_before_baseline=90))
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])

    def test_a_specimen_drawn_after_baseline_is_not_proposed(self):
        """It could belong to any later timepoint, so baseline is not
        the only candidate and nothing is proposed.
        """
        self.create_orphan(self.baseline_datetime + timedelta(days=30))
        row = self.get_row(get_df_orphan_results())
        self.assertTrue(pd.isna(row["candidate_rule"]))
        self.assertTrue(pd.isna(row["candidate_subject_visit_id"]))

    def test_nothing_is_proposed_where_there_is_no_subject(self):
        """With no subject there is no baseline to compare against."""
        self.create_orphan(self.baseline_datetime - timedelta(days=3), subject_identifier="")
        row = self.get_row(get_df_orphan_results())
        self.assertTrue(pd.isna(row["candidate_rule"]))

    def test_nothing_is_proposed_where_the_result_already_has_a_timepoint(self):
        self.create_orphan(
            self.baseline_datetime - timedelta(days=3),
            subject_visit=self.subject_visit,
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
        )
        row = self.get_row(get_df_orphan_results())
        self.assertTrue(pd.isna(row["candidate_rule"]))

    def test_nothing_is_proposed_where_the_specimen_has_no_datetime(self):
        self.create_orphan(None)
        row = self.get_row(get_df_orphan_results())
        self.assertTrue(pd.isna(row["candidate_rule"]))

    def test_names_the_requisition_waiting_at_baseline(self):
        """The payoff: the result could be linked to this."""
        requisition = self.create_requisition()
        self.create_orphan(self.baseline_datetime - timedelta(days=3))
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(str(requisition.id), row["candidate_requisition_id"])
        self.assertEqual(
            requisition.requisition_identifier, row["candidate_requisition_identifier"]
        )

    def test_no_requisition_at_baseline_leaves_the_candidate_empty(self):
        """The timepoint is proposed, but there is nothing to link to
        until someone keys the requisition.
        """
        self.create_orphan(self.baseline_datetime - timedelta(days=3))
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])
        self.assertTrue(pd.isna(row["candidate_requisition_id"]))

    def test_a_panel_with_no_requisition_at_baseline_is_not_matched(self):
        """The candidate requisition is looked up by panel, not just by
        timepoint.
        """
        self.create_requisition()
        self.create_orphan(self.baseline_datetime - timedelta(days=3), panel_name="lft")
        row = self.get_row(get_df_orphan_results())
        self.assertEqual(ON_OR_BEFORE_BASELINE, row["candidate_rule"])
        self.assertTrue(pd.isna(row["candidate_requisition_id"]))
