from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pandas as pd
from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone
from multisite import SiteID

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results_import.constants import (
    PANEL_NOT_EXPECTED,
    REQUISITION_NOT_KEYED,
    RESOLVER_MISS,
    VISIT_NOT_FOUND,
)
from edc_lab_results_import.dataframes import get_df_orphan_results
from edc_lab_results_import.models import Result
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.models import RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results_import")
@override_settings(SITE_ID=SiteID(10))
class TestOrphanResultsDataframe(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier

    def create_requisition(self, panel_name: str = "fbc") -> SubjectRequisition:
        return SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name=panel_name),
            requisition_datetime=self.subject_visit.report_datetime,
        )

    def create_orphan(
        self,
        utestid: str = "haemoglobin",
        panel_name: str = "fbc",
        visit_code: str | None = None,
        **kwargs,
    ) -> Result:
        """Create an imported result carrying no requisition."""
        opts = dict(
            subject_identifier=self.subject_identifier,
            screening_identifier="SCR0001",
            requisition=None,
            requisition_identifier="",
            visit_code=visit_code or self.subject_visit.visit_code,
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
            specimen_collected_datetime=self.subject_visit.report_datetime,
        )
        opts.update(**kwargs)
        return Result.objects.create(**opts)

    def set_entry_status(self, panel_name: str, entry_status: str) -> None:
        RequisitionMetadata.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name=panel_name,
        ).update(entry_status=entry_status)

    def test_returns_empty_frame_with_columns_when_nothing_is_orphaned(self):
        df = get_df_orphan_results()
        self.assertTrue(df.empty)
        self.assertIn("bucket", df.columns)
        self.assertIn("requisition_identifier", df.columns)

    def test_a_result_with_a_requisition_is_not_orphaned(self):
        requisition = self.create_requisition()
        self.create_orphan(
            requisition=requisition,
            requisition_identifier=requisition.requisition_identifier,
        )
        self.assertTrue(get_df_orphan_results().empty)

    def test_resolver_miss_where_the_requisition_already_exists(self):
        """The requisition is keyed, the importer's exact date join
        missed it. No data manager needed.
        """
        requisition = self.create_requisition()
        self.create_orphan()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(RESOLVER_MISS, row["bucket"])
        self.assertEqual(str(requisition.id), row["requisition_id"])
        self.assertEqual(requisition.requisition_identifier, row["requisition_identifier"])
        self.assertEqual(str(self.subject_visit.id), row["subject_visit_id"])

    def test_resolver_miss_found_even_when_the_specimen_predates_the_visit(self):
        """A screening draw captured at baseline. Nothing is matched on
        the date, so the gap does not stop the link being found.
        """
        self.create_requisition()
        self.create_orphan(
            specimen_collected_datetime=self.subject_visit.report_datetime - timedelta(days=3)
        )
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(RESOLVER_MISS, row["bucket"])
        self.assertEqual(-3, row["days_from_visit"])

    def test_requisition_not_keyed_is_the_worklist(self):
        self.set_entry_status("fbc", REQUIRED)
        self.create_orphan()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(REQUISITION_NOT_KEYED, row["bucket"])
        self.assertEqual(REQUIRED, row["entry_status"])
        self.assertTrue(pd.isna(row["requisition_id"]))

    def test_panel_not_expected_where_the_metadata_says_keyed_elsewhere(self):
        """No requisition and no metadata saying one is due here, so
        the utest id to panel mapping is the suspect.
        """
        RequisitionMetadata.objects.filter(
            subject_identifier=self.subject_identifier, panel_name="fbc"
        ).delete()
        self.create_orphan()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(PANEL_NOT_EXPECTED, row["bucket"])

    def test_a_keyed_requisition_metadata_row_does_not_make_a_worklist_item(self):
        """`entry_status` KEYED with no requisition at this timepoint
        means the metadata and the requisition disagree. Not a worklist
        item, but `entry_status` keeps it visible.
        """
        self.set_entry_status("fbc", KEYED)
        self.create_orphan()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(PANEL_NOT_EXPECTED, row["bucket"])
        self.assertEqual(KEYED, row["entry_status"])

    def test_visit_not_found_where_the_timepoint_matches_no_visit(self):
        self.create_orphan(visit_code="9999")
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(VISIT_NOT_FOUND, row["bucket"])

    def test_carries_the_schedule_from_the_related_visit(self):
        """`RequisitionMetadata` is keyed on the schedule, which the
        result does not carry. See `ResultImporter.df_related_visits`,
        which hardcodes one schedule name.
        """
        self.set_entry_status("fbc", REQUIRED)
        self.create_orphan()
        row = get_df_orphan_results().iloc[0]
        self.assertEqual(self.subject_visit.visit_schedule_name, row["visit_schedule_name"])
        self.assertEqual(self.subject_visit.schedule_name, row["schedule_name"])

    def test_worklist_grain_is_subject_timepoint_and_panel(self):
        """Many analytes, one requisition to key."""
        self.set_entry_status("fbc", REQUIRED)
        for utestid in ["haemoglobin", "wbc", "platelets"]:
            self.create_orphan(utestid=utestid)
        df = get_df_orphan_results()
        self.assertEqual(3, len(df))
        self.assertEqual(
            1,
            df.groupby(
                ["subject_identifier", "visit_code", "visit_code_sequence", "panel_name"]
            ).ngroups,
        )

    def test_metadata_exists_for_the_test_panel(self):
        """Guards the buckets above, which mean nothing if the visit
        schedule never created requisition metadata for this panel.
        """
        self.assertTrue(
            RequisitionMetadata.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_code=self.subject_visit.visit_code,
                panel_name="fbc",
                entry_status=REQUIRED,
            ).exists()
        )
