from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import INCOMPLETE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow
from pytz import timezone

from ...constants import DIABETES_CLINIC, HIV_CLINIC, HYPERTENSION_CLINIC
from ...forms import ClinicalReviewBaselineForm
from ..testcase_mixin import TestCaseMixin


def get_now():
    return get_utcnow().astimezone(timezone("Africa/Kampala"))


class TestClinicalReviewBaseline(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.baseline_datetime = get_utcnow() - relativedelta(months=1)

        # hiv clinic
        self.subject_screening_hiv = self.get_subject_screening(
            report_datetime=self.baseline_datetime, clinic_type=HIV_CLINIC
        )
        self.subject_consent_hiv = self.get_subject_consent(
            subject_screening=self.subject_screening_hiv,
            clinic_type=HIV_CLINIC,
            consent_datetime=self.baseline_datetime,
        )
        self.subject_visit_hiv = self.get_subject_visit(
            subject_screening=self.subject_screening_hiv,
            subject_consent=self.subject_consent_hiv,
            report_datetime=self.baseline_datetime,
        )

        # htn clinic
        self.subject_screening_htn = self.get_subject_screening(
            report_datetime=self.baseline_datetime,
            clinic_type=HYPERTENSION_CLINIC,
        )
        self.subject_consent_htn = self.get_subject_consent(
            subject_screening=self.subject_screening_htn,
            clinic_type=HYPERTENSION_CLINIC,
            report_datetime=self.baseline_datetime,
        )
        self.subject_visit_htn = self.get_subject_visit(
            subject_screening=self.subject_screening_htn,
            subject_consent=self.subject_consent_htn,
            report_datetime=self.baseline_datetime,
        )

        # diabetes clinic
        self.subject_screening_dm = self.get_subject_screening(
            report_datetime=self.baseline_datetime, clinic_type=DIABETES_CLINIC
        )
        self.subject_consent_dm = self.get_subject_consent(
            subject_screening=self.subject_screening_dm,
            clinic_type=DIABETES_CLINIC,
            report_datetime=self.baseline_datetime,
        )
        self.subject_visit_dm = self.get_subject_visit(
            subject_screening=self.subject_screening_dm,
            subject_consent=self.subject_consent_dm,
            report_datetime=self.baseline_datetime,
        )

    def test_form_ok_hiv(self):
        data = {
            "subject_visit": self.subject_visit_hiv.pk,
            "report_datetime": self.subject_visit_hiv.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": YES,
            "hiv_test_ago": "5y",
            "hiv_dx": YES,
            "htn_test": NO,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": NO,
            "dm_test_ago": None,
            "dm_dx": NOT_APPLICABLE,
            "health_insurance": YES,
            "patient_club": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_form_ok_hypertensive(self):
        data = {
            "subject_visit": self.subject_visit_htn.pk,
            "report_datetime": self.subject_visit_htn.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": YES,
            "htn_test_ago": "1y1m",
            "htn_dx": YES,
            "dm_test": NO,
            "dm_test_ago": None,
            "dm_dx": NOT_APPLICABLE,
            "health_insurance": YES,
            "patient_club": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_form_ok_dm(self):
        data = {
            "subject_visit": self.subject_visit_dm.pk,
            "report_datetime": self.subject_visit_dm.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": NO,
            "htn_test_ago": None,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": YES,
            "dm_test_ago": "1y1m",
            "dm_dx": YES,
            "health_insurance": YES,
            "patient_club": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_hiv_if_hiv_clinic(self):
        data = {
            "subject_visit": self.subject_visit_hiv.pk,
            "report_datetime": self.subject_visit_hiv.report_datetime,
            "crf_status": INCOMPLETE,
        }
        data.update(
            hiv_test=NO,
            hiv_test_ago=None,
            hiv_test_date=None,
            hiv_dx=NOT_APPLICABLE,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertIn("hiv_test", form._errors)

        data.update(
            hiv_test=YES,
            hiv_test_ago=None,
            hiv_test_date=None,
            hiv_dx=NO,
            dm_test=NO,
            htn_test=NO,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
        self.assertIn("hiv_dx", form._errors)

        data.update(
            hiv_test=YES,
            hiv_test_ago=None,
            hiv_test_date=None,
            hiv_dx=NOT_APPLICABLE,
            dm_test=NO,
            htn_test=NO,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
        self.assertIn("hiv_dx", form._errors)

        data.update(
            hiv_test=YES,
            hiv_test_ago=None,
            hiv_test_date=None,
            hiv_dx=YES,
            dm_test=NO,
            htn_test=NO,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
        self.assertNotIn("hiv_dx", form._errors)
        self.assertIn("__all__", form._errors)

        data.update(
            hiv_test=YES,
            hiv_test_ago=None,
            hiv_test_date=get_utcnow(),
            hiv_dx=YES,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
        self.assertNotIn("hiv_dx", form._errors)
        self.assertNotIn("__all__", form._errors)

        data.update(hiv_test=YES, hiv_test_ago="10y", hiv_test_date=None, hiv_dx=YES)
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
        self.assertNotIn("hiv_dx", form._errors)
        self.assertNotIn("__all__", form._errors)

    def test_htn_if_htn_clinic(self):
        data = {
            "subject_visit": self.subject_visit_htn.pk,
            "report_datetime": self.subject_visit_htn.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": NO,
            "htn_test_ago": "1y",
            "htn_dx": NOT_APPLICABLE,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertIn("htn_test", form._errors)

        data.update(
            htn_test=YES,
            htn_dx=NOT_APPLICABLE,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("htn_test", form._errors)
        self.assertIn("htn_dx", form._errors)

        data.update(
            htn_test=YES,
            htn_dx=YES,
        )
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertNotIn("htn_test", form._errors)
        self.assertNotIn("htn_dx", form._errors)

    def test_dm_if_ncd_clinic(self):
        for cond in ["dm", "htn"]:
            data = {
                "subject_visit": self.subject_visit_ncd.pk,
                "report_datetime": self.subject_visit_ncd.report_datetime,
                "crf_status": INCOMPLETE,
                "hiv_test": NO,
                "hiv_test_ago": None,
                "hiv_dx": NOT_APPLICABLE,
                "dm_test": NO,
                "dm_dx": NOT_APPLICABLE,
                "htn_test": NO,
                "htn_dx": NOT_APPLICABLE,
            }
            with self.subTest(cond=cond):
                form = ClinicalReviewBaselineForm(data=data)
                form.is_valid()
                # expects a test
                self.assertIn("__all__", [k for k in form._errors.keys()])

                data.update(
                    {
                        f"{cond}_test": YES,
                        f"{cond}_test_ago": "1y",
                        f"{cond}_dx": NOT_APPLICABLE,
                    }
                )
                form = ClinicalReviewBaselineForm(data=data)
                form.is_valid()
                # expects a diagnosis
                self.assertIn("__all__", [k for k in form._errors.keys()])

                data.update({f"{cond}_test": YES, f"{cond}_test_ago": "1y", f"{cond}_dx": YES})
                form = ClinicalReviewBaselineForm(data=data)
                form.is_valid()
                self.assertNotIn("__all__", [k for k in form._errors.keys()])
                self.assertNotIn(f"{cond}_test", form._errors)
                self.assertNotIn(cond, form._errors)
