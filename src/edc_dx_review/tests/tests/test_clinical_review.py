from copy import deepcopy

from django.test import TestCase, override_settings, tag
from edc_constants.constants import (
    CHOL,
    DM,
    HIV,
    HTN,
    INCOMPLETE,
    NO,
    NOT_APPLICABLE,
    YES,
)
from edc_dx.utils import DiagnosisLabelError

from edc_dx_review.forms import ClinicalReviewFollowupForm

from ..forms import ClinicalReviewBaselineForm
from ..test_case_mixin import TestCaseMixin


class TestClinicalReview(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = self.enroll()
        self.create_visits(self.subject_identifier)

        self.baseline_data = {
            "subject_visit": self.subject_visit_baseline.pk,
            "report_datetime": self.subject_visit_baseline.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": YES,
            "hiv_test_ago": "5y",
            "hiv_dx": YES,
            "htn_test": NO,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": NO,
            "dm_dx": NOT_APPLICABLE,
            "chol_test": NO,
            "chol_dx": NOT_APPLICABLE,
            "complications": NO,
        }

        self.followup_data = {
            "subject_visit": self.subject_visit_followup.pk,
            "report_datetime": self.subject_visit_followup.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": YES,
            "hiv_test_ago": "5y",
            "hiv_dx": YES,
            "htn_test": NO,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": NO,
            "dm_dx": NOT_APPLICABLE,
            "chol_test": NO,
            "chol_dx": NOT_APPLICABLE,
            "complications": NO,
        }

    @tag("1")
    @override_settings(EDC_DIAGNOSIS_LABELS={HIV: "HIV"})
    def test_baseline_form_ok(self):
        """Tests validation respects DIAGNOSIS LABELS"""
        form = ClinicalReviewBaselineForm(data=self.baseline_data)
        form.is_valid()
        self.assertEqual(form._errors, {})
        obj = form.save()
        self.assertIsNotNone(obj.hiv_test_estimated_date)
        self.assertIsNone(obj.htn_test_estimated_date)
        self.assertIsNone(obj.dm_test_estimated_date)
        self.assertIsNone(obj.chol_test_estimated_date)

    @tag("1")
    @override_settings(EDC_DIAGNOSIS_LABELS={HIV: "HIV"})
    def test_baseline_unknown_label_raises(self):
        data = deepcopy(self.baseline_data)
        data.update(
            {
                "htn_test": YES,
                "htn_test_ago": "1y2m",
                "htn_dx": YES,
            }
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})
        # response to htn fields is unexpected
        self.assertRaises(DiagnosisLabelError, form.save)

    @tag("1")
    @override_settings(EDC_DIAGNOSIS_LABELS={HIV: "HIV", HTN: "htn"})
    def test_baseline_known_label_does_not_raise(self):
        data = deepcopy(self.baseline_data)
        data.update(
            {
                "htn_test": YES,
                "htn_test_ago": "1y2m",
                "htn_dx": YES,
            }
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})
        try:
            form.save()
        except DiagnosisLabelError:
            self.fail("DiagnosisLabelError unexpectedly raised")

    @tag("1")
    @override_settings(
        EDC_DIAGNOSIS_LABELS={
            HIV: "HIV",
            HTN: "Hypertensive",
            DM: "diabetic",
            CHOL: "High Cholesteral",
        }
    )
    def test_baseline_all_labels(self):
        data = deepcopy(self.baseline_data)
        data.update(
            {
                "htn_test": YES,
                "htn_test_ago": "1y2m",
                "htn_dx": YES,
                "dm_test": YES,
                "dm_test_ago": "1y2m",
                "dm_dx": YES,
                "chol_test": YES,
                "chol_test_ago": "1y2m",
                "chol_dx": YES,
            }
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    @tag("1")
    @override_settings(
        EDC_DIAGNOSIS_LABELS={
            HIV: "HIV",
            HTN: "Hypertensive",
        }
    )
    def test_baseline_requires_date_or_ago(self):
        """Assert raises if neither a date nor an `ago` is provided"""
        data = deepcopy(self.baseline_data)
        data.update(
            {
                "htn_test": YES,
                "htn_test_ago": None,
                "htn_test_date": None,
                "htn_dx": YES,
            }
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertIn("Htn: When was the ", str([form._errors.get("__all__")]))

    @tag("1")
    @override_settings(
        EDC_DIAGNOSIS_LABELS={
            HIV: "HIV",
        }
    )
    def test_baseline_allowed_at_baseline_only(self):
        data = deepcopy(self.baseline_data)
        data.update(
            {
                "subject_visit": self.subject_visit_followup.pk,
                "report_datetime": self.subject_visit_followup.report_datetime,
            }
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertIn(
            "This form is only available for completion at baseline",
            str([form._errors.get("__all__")]),
        )

    @tag("1")
    @override_settings(EDC_DIAGNOSIS_LABELS={HIV: "HIV"})
    def test_followup_requires_baseline_review(self):
        form = ClinicalReviewFollowupForm(data=self.followup_data)
        form.is_valid()
        self.assertIn(
            "Please complete Clinical Review: Baseline",
            str([form._errors.get("__all__")]),
        )

    @tag("1")
    @override_settings(EDC_DIAGNOSIS_LABELS={HIV: "HIV"})
    def test_followup_ok(self):
        form = ClinicalReviewBaselineForm(data=self.baseline_data)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()

        form = ClinicalReviewFollowupForm(data=self.followup_data)
        form.is_valid()
        self.assertIn("Complete the `HIV Initial Review`", str(form._errors.get("__all__")))

        # form = HivInitialReviewForm(data=self.followup_data)
        # obj = form.save()
        # self.assertIsNotNone(obj.hiv_test_estimated_date)
        # self.assertIsNone(obj.htn_test_estimated_date)
        # self.assertIsNone(obj.dm_test_estimated_date)
        # self.assertIsNone(obj.chol_test_estimated_date)

    # def test_form_ok_hypertensive(self):
    #     data = {
    #         "subject_visit": self.subject_visit_htn.pk,
    #         "report_datetime": self.subject_visit_htn.report_datetime,
    #         "crf_status": INCOMPLETE,
    #         "hiv_test": NO,
    #         "hiv_test_ago": None,
    #         "hiv_dx": NOT_APPLICABLE,
    #         "htn_test": YES,
    #         "htn_test_ago": "1y1m",
    #         "htn_dx": YES,
    #         "dm_test": NO,
    #         "dm_test_ago": None,
    #         "dm_dx": NOT_APPLICABLE,
    #         "health_insurance": YES,
    #         "patient_club": YES,
    #     }
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertEqual(form._errors, {})
    #
    # def test_form_ok_dm(self):
    #     data = {
    #         "subject_visit": self.subject_visit_dm.pk,
    #         "report_datetime": self.subject_visit_dm.report_datetime,
    #         "crf_status": INCOMPLETE,
    #         "hiv_test": NO,
    #         "hiv_test_ago": None,
    #         "hiv_dx": NOT_APPLICABLE,
    #         "htn_test": NO,
    #         "htn_test_ago": None,
    #         "htn_dx": NOT_APPLICABLE,
    #         "dm_test": YES,
    #         "dm_test_ago": "1y1m",
    #         "dm_dx": YES,
    #         "health_insurance": YES,
    #         "patient_club": YES,
    #     }
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertEqual(form._errors, {})
    #
    # def test_hiv_if_hiv_clinic(self):
    #     data = {
    #         "subject_visit": self.subject_visit_hiv.pk,
    #         "report_datetime": self.subject_visit_hiv.report_datetime,
    #         "crf_status": INCOMPLETE,
    #     }
    #     data.update(
    #         hiv_test=NO,
    #         hiv_test_ago=None,
    #         hiv_test_date=None,
    #         hiv_dx=NOT_APPLICABLE,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertIn("hiv_test", form._errors)
    #
    #     data.update(
    #         hiv_test=YES,
    #         hiv_test_ago=None,
    #         hiv_test_date=None,
    #         hiv_dx=NO,
    #         dm_test=NO,
    #         htn_test=NO,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("hiv_test", form._errors)
    #     self.assertIn("hiv_dx", form._errors)
    #
    #     data.update(
    #         hiv_test=YES,
    #         hiv_test_ago=None,
    #         hiv_test_date=None,
    #         hiv_dx=NOT_APPLICABLE,
    #         dm_test=NO,
    #         htn_test=NO,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("hiv_test", form._errors)
    #     self.assertIn("hiv_dx", form._errors)
    #
    #     data.update(
    #         hiv_test=YES,
    #         hiv_test_ago=None,
    #         hiv_test_date=None,
    #         hiv_dx=YES,
    #         dm_test=NO,
    #         htn_test=NO,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("hiv_test", form._errors)
    #     self.assertNotIn("hiv_dx", form._errors)
    #     self.assertIn("__all__", form._errors)
    #
    #     data.update(
    #         hiv_test=YES,
    #         hiv_test_ago=None,
    #         hiv_test_date=get_utcnow(),
    #         hiv_dx=YES,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("hiv_test", form._errors)
    #     self.assertNotIn("hiv_dx", form._errors)
    #     self.assertNotIn("__all__", form._errors)
    #
    #     data.update(hiv_test=YES, hiv_test_ago="10y", hiv_test_date=None, hiv_dx=YES)
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("hiv_test", form._errors)
    #     self.assertNotIn("hiv_dx", form._errors)
    #     self.assertNotIn("__all__", form._errors)
    #
    # def test_htn_if_htn_clinic(self):
    #     data = {
    #         "subject_visit": self.subject_visit_htn.pk,
    #         "report_datetime": self.subject_visit_htn.report_datetime,
    #         "crf_status": INCOMPLETE,
    #         "hiv_test": NO,
    #         "hiv_test_ago": None,
    #         "hiv_dx": NOT_APPLICABLE,
    #         "htn_test": NO,
    #         "htn_test_ago": "1y",
    #         "htn_dx": NOT_APPLICABLE,
    #     }
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertIn("htn_test", form._errors)
    #
    #     data.update(
    #         htn_test=YES,
    #         htn_dx=NOT_APPLICABLE,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("htn_test", form._errors)
    #     self.assertIn("htn_dx", form._errors)
    #
    #     data.update(
    #         htn_test=YES,
    #         htn_dx=YES,
    #     )
    #     form = ClinicalReviewBaselineForm(data=data)
    #     form.is_valid()
    #     self.assertNotIn("htn_test", form._errors)
    #     self.assertNotIn("htn_dx", form._errors)
    #
    # def test_dm_if_ncd_clinic(self):
    #     for cond in ["dm", "htn"]:
    #         data = {
    #             "subject_visit": self.subject_visit_ncd.pk,
    #             "report_datetime": self.subject_visit_ncd.report_datetime,
    #             "crf_status": INCOMPLETE,
    #             "hiv_test": NO,
    #             "hiv_test_ago": None,
    #             "hiv_dx": NOT_APPLICABLE,
    #             "dm_test": NO,
    #             "dm_dx": NOT_APPLICABLE,
    #             "htn_test": NO,
    #             "htn_dx": NOT_APPLICABLE,
    #         }
    #         with self.subTest(cond=cond):
    #             form = ClinicalReviewBaselineForm(data=data)
    #             form.is_valid()
    #             # expects a test
    #             self.assertIn("__all__", [k for k in form._errors.keys()])
    #
    #             data.update(
    #                 {
    #                     f"{cond}_test": YES,
    #                     f"{cond}_test_ago": "1y",
    #                     f"{cond}_dx": NOT_APPLICABLE,
    #                 }
    #             )
    #             form = ClinicalReviewBaselineForm(data=data)
    #             form.is_valid()
    #             # expects a diagnosis
    #             self.assertIn("__all__", [k for k in form._errors.keys()])
    #
    #             data.update({f"{cond}_test": YES, f"{cond}_test_ago": "1y", f"{cond}_dx": YES})
    #             form = ClinicalReviewBaselineForm(data=data)
    #             form.is_valid()
    #             self.assertNotIn("__all__", [k for k in form._errors.keys()])
    #             self.assertNotIn(f"{cond}_test", form._errors)
    #             self.assertNotIn(cond, form._errors)
