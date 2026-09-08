from __future__ import annotations

from decimal import Decimal

import pandas as pd
from clinicedc_constants import (
    FEMALE,
    GRAMS_PER_DECILITER,
    GRAMS_PER_LITER,
    NO,
    YES,
)
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import BloodResultsFbc, SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results.utils import get_utest_ids
from edc_lab_results_import.constants import DIFFERS, MATCH, NOT_COMPARED
from edc_lab_results_import.dataframes import get_df_result_comparison
from edc_lab_results_import.models import Result
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results_import")
@override_settings(SITE_ID=10)
class TestResultComparisonDataframe(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name="fbc"),
            requisition_datetime=self.subject_visit.report_datetime,
        )

    def create_crf(self, **kwargs) -> BloodResultsFbc:
        opts = dict(subject_visit=self.subject_visit, requisition=self.requisition)
        opts.update(**kwargs)
        return BloodResultsFbc.objects.create(**opts)

    def create_result(
        self,
        utestid: str,
        result_value: Decimal | None = None,
        units: str | None = None,
        flag: str | None = None,
        source_file: str | None = None,
        with_requisition: bool = True,
        **kwargs,
    ) -> Result:
        opts = dict(
            subject_identifier=self.subject_identifier,
            screening_identifier="SCR0001",
            subject_visit=self.subject_visit,
            requisition=self.requisition if with_requisition else None,
            requisition_identifier=(
                self.requisition.requisition_identifier if with_requisition else ""
            ),
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name="fbc",
            source_file=source_file or "report_001.pdf",
            utestid=utestid,
            source_utestid=utestid.upper(),
            result_value=result_value,
            units=units or "",
            flag=flag or "",
            result_no=f"RES-{utestid}-{source_file or 'report_001.pdf'}",
            order_no="ORD001",
            sample_no="SAM001",
            result_status="final",
            name_id="NAME001",
            result_datetime=timezone.now(),
        )
        opts.update(**kwargs)
        return Result.objects.create(**opts)

    @staticmethod
    def get_row(df, utestid: str, **filters):
        rows = df[df["utestid"] == utestid]
        for column, value in filters.items():
            rows = rows[rows[column] == value]
        return rows.iloc[0]

    def test_returns_empty_frame_with_columns_when_no_crfs(self):
        self.create_result("haemoglobin", result_value=Decimal("13.4"))
        df = get_df_result_comparison()
        self.assertTrue(df.empty)
        self.assertIn("value_status", df.columns)
        self.assertIn("pct_diff", df.columns)

    def test_grid_covers_every_utestid_on_the_crf(self):
        self.create_crf()
        self.create_result("haemoglobin", result_value=Decimal("13.4"))
        df = get_df_result_comparison()
        self.assertEqual(sorted(get_utest_ids(BloodResultsFbc)), sorted(df["utestid"]))

    def test_imported_utestid_not_on_the_crf_is_left_out(self):
        self.create_crf()
        self.create_result("creatinine", result_value=Decimal(53))
        df = get_df_result_comparison()
        self.assertNotIn("creatinine", list(df["utestid"]))

    def test_matching_value_has_no_rounding_noise(self):
        """The imported value carries four decimal places, the CRF two."""
        self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4000"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(MATCH, row["value_status"])
        self.assertEqual(MATCH, row["units_status"])
        self.assertEqual(0.0, row["abs_diff"])
        self.assertEqual(0.0, row["pct_diff"])
        self.assertEqual(1.0, row["ratio"])

    def test_a_difference_is_measured_three_ways(self):
        self.create_crf(
            haemoglobin_value=Decimal("13.5"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(DIFFERS, row["value_status"])
        self.assertAlmostEqual(0.1, row["abs_diff"], places=6)
        self.assertAlmostEqual(100 * 0.1 / 13.4, row["pct_diff"], places=6)
        self.assertAlmostEqual(13.4 / 13.5, row["ratio"], places=6)

    def test_ratio_finds_a_decimal_point_slip(self):
        """A ratio at a power of ten is the signal a percentage
        difference buries among the large differences.
        """
        self.create_crf(
            haemoglobin_value=Decimal("1.34"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(DIFFERS, row["value_status"])
        self.assertAlmostEqual(10.0, row["ratio"], places=6)

    def test_a_units_mismatch_is_not_compared_by_value(self):
        self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result("haemoglobin", result_value=Decimal(134), units=GRAMS_PER_LITER)
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(NOT_COMPARED, row["value_status"])
        self.assertEqual(DIFFERS, row["units_status"])
        self.assertTrue(pd.isna(row["comparable_value"]))
        self.assertTrue(pd.isna(row["abs_diff"]))

    def test_uses_the_converted_value_where_it_matches_the_crf_units(self):
        self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin",
            result_value=Decimal(134),
            units=GRAMS_PER_LITER,
            converted_result_value=Decimal("13.4"),
            converted_units=GRAMS_PER_DECILITER,
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(MATCH, row["value_status"])
        self.assertEqual(13.4, row["comparable_value"])

    def test_abnormal_flag_is_compared(self):
        self.create_crf(haemoglobin_abnormal=NO)
        self.create_result("haemoglobin", flag="H")
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(YES, row["abnormal"])
        self.assertEqual(DIFFERS, row["abnormal_status"])

    def test_crf_value_with_no_imported_result(self):
        """The panel was imported, but not this utest id."""
        self.create_crf(haemoglobin_value=Decimal("13.4"), wbc_value=Decimal("5.6"))
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "wbc")
        self.assertEqual(0, row["n_imported_for_key"])
        self.assertTrue(row["panel_imported"])
        self.assertEqual(NOT_COMPARED, row["value_status"])
        self.assertEqual(NOT_COMPARED, row["units_status"])
        self.assertEqual(NOT_COMPARED, row["abnormal_status"])
        self.assertTrue(pd.isna(row["join_key"]))

    def test_a_panel_never_imported_at_all(self):
        """No source document reached this requisition."""
        self.create_crf(haemoglobin_value=Decimal("13.4"))
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual(0, row["n_imported_for_key"])
        self.assertFalse(row["panel_imported"])

    def test_both_sides_blank_is_kept(self):
        self.create_crf()
        df = get_df_result_comparison()
        self.assertEqual(len(get_utest_ids(BloodResultsFbc)), len(df))
        self.assertTrue(df["crf_value"].isna().all())

    def test_falls_back_to_the_related_visit_where_there_is_no_requisition(self):
        """A baseline result is not always imported against a
        requisition. See `join_key`.
        """
        self.create_crf(
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
        )
        self.create_result(
            "haemoglobin",
            result_value=Decimal("13.4"),
            units=GRAMS_PER_DECILITER,
            with_requisition=False,
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual("subject_visit", row["join_key"])
        self.assertEqual(MATCH, row["value_status"])

    def test_falls_back_where_the_crf_has_no_requisition(self):
        """The requisition is cleared with `update` rather than
        `create`, which cannot save a result CRF with no requisition.
        See `get_reference_range_collection`.
        """
        obj = self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        BloodResultsFbc.objects.filter(pk=obj.pk).update(requisition=None)
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual("subject_visit", row["join_key"])
        self.assertEqual(MATCH, row["value_status"])

    def test_joins_on_requisition_first(self):
        self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
        )
        row = self.get_row(get_df_result_comparison(), "haemoglobin")
        self.assertEqual("requisition", row["join_key"])

    def test_a_corrected_report_keeps_both_rows(self):
        """Two source files against one requisition are never merged."""
        self.create_crf(
            haemoglobin_value=Decimal("13.4"), haemoglobin_units=GRAMS_PER_DECILITER
        )
        self.create_result(
            "haemoglobin",
            result_value=Decimal("13.4"),
            units=GRAMS_PER_DECILITER,
            source_file="report_001.pdf",
        )
        self.create_result(
            "haemoglobin",
            result_value=Decimal("13.9"),
            units=GRAMS_PER_DECILITER,
            source_file="report_002_corrected.pdf",
        )
        df = get_df_result_comparison()
        rows = df[df["utestid"] == "haemoglobin"]
        self.assertEqual(2, len(rows))
        self.assertEqual({2}, set(rows["n_imported_for_key"]))
        self.assertEqual(
            {MATCH, DIFFERS},
            set(rows["value_status"]),
        )
