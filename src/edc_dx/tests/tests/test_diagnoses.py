from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import CHOL, DM, HIV, HTN, NOT_APPLICABLE, POS, YES
from model_bakery import baker

from edc_dx.diagnoses import (
    ClinicalReviewBaselineRequired,
    Diagnoses,
    InitialReviewRequired,
    MultipleInitialReviewsExist,
)

from ..test_case_mixin import TestCaseMixin


class TestDiagnoses(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = self.enroll()
        self.create_visits(self.subject_identifier)

    def test_diagnoses_no_baseline_review_raises(self):
        self.assertRaises(
            ClinicalReviewBaselineRequired,
            Diagnoses,
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )

        clinical_review_baseline = baker.make(
            "edc_dx_review.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_test=YES,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        try:
            diagnoses = Diagnoses(
                subject_identifier=self.subject_visit_baseline.subject_identifier,
            )
        except ClinicalReviewBaselineRequired:
            self.fail("DiagnosesError unexpectedly raised")

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNone(diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(DM))

        clinical_review_baseline.htn_test = YES
        clinical_review_baseline.htn_test_ago = "1y"
        clinical_review_baseline.htn_dx = YES
        clinical_review_baseline.save()

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )
        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(YES, diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(DM))

        clinical_review_baseline.dm_test = YES
        clinical_review_baseline.dm_test_ago = "1y"
        clinical_review_baseline.dm_dx = YES
        clinical_review_baseline.save()

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )
        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(YES, diagnoses.get_dx(HTN))
        self.assertEqual(YES, diagnoses.get_dx(DM))

    def test_diagnoses_dates_baseline_raises(self):
        """Assert expects the initial review model instance before
        returning a dx.
        """

        for prefix in [HIV, DM, HTN, CHOL]:
            prefix = prefix.lower()
            opts = {
                "subject_visit": self.subject_visit_baseline,
                f"{prefix}_test": POS,
                f"{prefix}_dx": YES,
                f"{prefix}_test_ago": "5y",
            }
            obj = baker.make("edc_dx_review.clinicalreviewbaseline", **opts)
            diagnoses = Diagnoses(
                subject_identifier=self.subject_visit_baseline.subject_identifier,
            )
            self.assertRaises(InitialReviewRequired, diagnoses.get_dx_date, HIV)
            obj.delete()

    def test_diagnoses_dates_baseline(self):

        clinical_review_baseline = baker.make(
            "edc_dx_review.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        baker.make(
            "edc_dx_review.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )
        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
            report_datetime=self.subject_visit_baseline.report_datetime,
            lte=True,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
            report_datetime=self.subject_visit_baseline.report_datetime,
            lte=False,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

    def test_diagnoses_dates(self):

        baker.make(
            "edc_dx_review.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )

        hiv_initial_review = baker.make(
            "edc_dx_review.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )

        self.subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit_baseline.appointment.save()
        self.subject_visit_baseline.appointment.refresh_from_db()
        self.subject_visit_baseline.refresh_from_db()

        baker.make(
            "edc_dx_review.clinicalreview",
            subject_visit=self.subject_visit_followup,
            hiv_test=NOT_APPLICABLE,
            hiv_dx=NOT_APPLICABLE,
            hiv_test_date=None,
            htn_test=YES,
            htn_dx=YES,
            htn_test_date=self.subject_visit_followup.report_datetime,
        )

        htn_initial_review = baker.make(
            "edc_dx_review.htninitialreview",
            subject_visit=self.subject_visit_followup,
            dx_ago=None,
            dx_date=self.subject_visit_followup.report_datetime,
        )

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_followup.subject_identifier,
            report_datetime=self.subject_visit_followup.report_datetime,
            lte=True,
        )
        self.assertIsNotNone(diagnoses.get_dx_date(HIV))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            hiv_initial_review.get_best_dx_date().date(),
        )

        self.assertEqual(
            diagnoses.get_dx_date(HTN),
            htn_initial_review.get_best_dx_date().date(),
        )
        self.assertIsNotNone(diagnoses.get_dx_date(HTN))

    def test_diagnoses_dates_baseline2(self):

        baker.make(
            "edc_dx_review.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        baker.make(
            "edc_dx_review.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )
        self.subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit_baseline.appointment.save()
        self.subject_visit_baseline.appointment.refresh_from_db()
        self.subject_visit_baseline.refresh_from_db()

        baker.make(
            "edc_dx_review.hivinitialreview",
            subject_visit=self.subject_visit_followup,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )
        self.assertRaises(MultipleInitialReviewsExist, getattr, diagnoses, "initial_reviews")
