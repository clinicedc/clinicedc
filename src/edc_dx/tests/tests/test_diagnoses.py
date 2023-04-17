from django.test import TestCase, override_settings
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import DM, HIV, HTN, NOT_APPLICABLE, YES
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
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
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

        clinical_review_baseline.htn_dx = YES
        clinical_review_baseline.save()

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )
        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(YES, diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(DM))

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

        for prefix in [HIV, DM, HTN]:
            prefix = prefix.lower()
            opts = {
                "subject_visit": self.subject_visit_baseline,
                f"{prefix}_dx": YES,
            }
            obj = baker.make("dx_app.clinicalreviewbaseline", **opts)
            diagnoses = Diagnoses(
                subject_identifier=self.subject_visit_baseline.subject_identifier,
            )
            self.assertRaises(InitialReviewRequired, diagnoses.get_dx_date, HIV)
            obj.delete()

    def test_diagnoses_dates_baseline(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
        )
        baker.make(
            "dx_app.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )
        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNotNone(diagnoses.get_dx_date(HIV))
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
            report_datetime=self.subject_visit_baseline.report_datetime,
            lte=True,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNotNone(diagnoses.get_dx_date(HIV))
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
            report_datetime=self.subject_visit_baseline.report_datetime,
            lte=False,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNotNone(diagnoses.get_dx_date(HIV))
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))

    def test_diagnoses_dates(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
        )

        hiv_initial_review = baker.make(
            "dx_app.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )

        self.subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit_baseline.appointment.save()
        self.subject_visit_baseline.appointment.refresh_from_db()
        self.subject_visit_baseline.refresh_from_db()

        baker.make(
            "dx_app.clinicalreview",
            subject_visit=self.subject_visit_followup,
            hiv_dx=NOT_APPLICABLE,
            htn_dx=YES,
        )

        htn_initial_review = baker.make(
            "dx_app.htninitialreview",
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
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
        )
        baker.make(
            "dx_app.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )
        self.subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit_baseline.appointment.save()
        self.subject_visit_baseline.appointment.refresh_from_db()
        self.subject_visit_baseline.refresh_from_db()

    @override_settings(
        EDC_DX_REVIEW_EXTRA_ATTRS={"initialreview": "initialreviewmissingsingleton"}
    )
    def test_diagnoses_dates_baseline3(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
        )

        baker.make(
            "dx_app.hivinitialreviewmissingsingleton",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )

        baker.make(
            "dx_app.hivinitialreviewmissingsingleton",
            subject_visit=self.subject_visit_followup,
            dx_ago="5y",
            rx_init_ago="4y",
        )

        diagnoses = Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
        )
        self.assertRaises(MultipleInitialReviewsExist, getattr, diagnoses, "initial_reviews")
