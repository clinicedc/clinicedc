from __future__ import annotations

from decimal import Decimal

from clinicedc_constants import FEMALE, GRAMS_PER_DECILITER, NO
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import BloodResultsFbc, SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from multisite import SiteID

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results.dataframes import get_df_result_crfs
from edc_lab_results.utils import get_utest_ids
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab_results")
@override_settings(SITE_ID=SiteID(10))
class TestResultCrfsDataframe(TestCase):
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

    def test_returns_empty_frame_with_columns_when_no_crfs(self):
        df = get_df_result_crfs()
        self.assertTrue(df.empty)
        self.assertIn("crf_value", df.columns)
        self.assertIn("decimal_places", df.columns)

    def test_one_row_per_utestid_including_the_blank_ones(self):
        """The frame is a grid of what could have been keyed, not only
        what was.
        """
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
        )
        df = get_df_result_crfs()
        utest_ids = get_utest_ids(BloodResultsFbc)
        self.assertEqual(len(utest_ids), len(df))
        self.assertEqual(sorted(utest_ids), sorted(df["utestid"]))
        blank = df[df["utestid"] != "haemoglobin"]
        self.assertTrue(blank["crf_value"].isna().all())

    def test_carries_value_units_abnormal_and_decimal_places(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
        )
        df = get_df_result_crfs()
        row = df[df["utestid"] == "haemoglobin"].iloc[0]
        self.assertEqual(13.4, row["crf_value"])
        self.assertEqual(GRAMS_PER_DECILITER, row["crf_units"])
        self.assertEqual(NO, row["crf_abnormal"])
        self.assertEqual(2, row["decimal_places"])
        self.assertEqual("fbc", row["panel_name"])
        self.assertEqual(BloodResultsFbc._meta.label_lower, row["crf_model"])

    def test_carries_the_subject_and_timepoint(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit, requisition=self.requisition
        )
        df = get_df_result_crfs()
        row = df.iloc[0]
        self.assertEqual(self.subject_identifier, row["subject_identifier"])
        self.assertEqual(self.subject_visit.visit_code, row["visit_code"])
        self.assertEqual(str(self.requisition.id), row["requisition_id"])

    def test_a_crf_with_no_requisition_keeps_its_row(self):
        """Baseline results are not always drawn against a requisition.

        The requisition is cleared with `update` rather than `create`,
        which cannot save a result CRF with no requisition. See
        `get_reference_range_collection`.
        """
        obj = BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit, requisition=self.requisition
        )
        BloodResultsFbc.objects.filter(pk=obj.pk).update(requisition=None)
        df = get_df_result_crfs()
        self.assertEqual(len(get_utest_ids(BloodResultsFbc)), len(df))
        self.assertTrue(df["requisition_id"].isna().all())
