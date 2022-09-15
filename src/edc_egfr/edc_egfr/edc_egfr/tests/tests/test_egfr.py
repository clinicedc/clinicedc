from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_constants.constants import BLACK, MALE
from edc_lab import site_labs
from edc_lab.models import Panel
from edc_lab_panel.panels import rft_panel
from edc_registration.models import RegisteredSubject
from edc_reportable import (
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    site_reportables,
)
from edc_reportable.grading_data.daids_july_2017 import grading_data
from edc_reportable.normal_data.africa import normal_data
from edc_utils import get_utcnow
from edc_utils.round_up import round_half_away_from_zero

from edc_egfr.calculators import EgfrCalculatorError
from edc_egfr.egfr import Egfr, EgfrError
from egfr_app.lab_profiles import lab_profile
from egfr_app.models import (
    Appointment,
    EgfrDropNotification,
    ResultCrf,
    SubjectRequisition,
    SubjectVisit,
)


class TestEgfr(TestCase):
    def setUp(self) -> None:
        RegisteredSubject.objects.create(
            subject_identifier="1234",
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=30),
            ethnicity=BLACK,
        )

    @classmethod
    def setUpTestData(cls):
        site_reportables._registry = {}
        site_reportables.register(
            name="my_reference_list", normal_data=normal_data, grading_data=grading_data
        )
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)

    def test_ok(self):
        egfr = Egfr(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=52.0,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

        try:
            self.assertGreater(egfr.egfr_value, 0.0)
        except EgfrCalculatorError as e:
            self.fail(e)

        try:
            self.assertIsNone(egfr.egfr_grade)
        except EgfrCalculatorError as e:
            self.fail(e)

        try:
            self.assertGreaterEqual(egfr.egfr_drop_value, 0.0)
        except EgfrCalculatorError as e:
            self.fail(e)

        try:
            self.assertIsNone(egfr.egfr_drop_grade)
        except EgfrCalculatorError as e:
            self.fail(e)

    def test_egfr_invalid_calculator(self):
        self.assertRaises(
            EgfrError,
            Egfr,
            gender=MALE,
            age_in_years=25,
            ethnicity=BLACK,
            creatinine_value=10.15,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
        )

    def test_egfr_missing_age_and_dob_raises(self):
        self.assertRaises(
            EgfrError,
            Egfr,
            gender=MALE,
            ethnicity=BLACK,
            creatinine_value=10.15,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

    def test_egfr_percent_drop_less_than_one_raises(self):
        self.assertRaises(
            EgfrError,
            Egfr,
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=10.15,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            report_datetime=get_utcnow(),
            percent_drop_threshold=0.25,
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

    def test_egfr_assay_datetime(self):
        self.assertRaises(
            EgfrError,
            Egfr,
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=10.15,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            report_datetime=get_utcnow(),
            assay_datetime=get_utcnow(),
            percent_drop_threshold=0.25,
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

    def test_egfr_grade(self):
        egfr = Egfr(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=275,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

        self.assertEqual(egfr.egfr_grade, 4)

    def test_egfr_dob(self):
        egfr = Egfr(
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=30),
            ethnicity=BLACK,
            creatinine_value=275,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )
        self.assertEqual(egfr.egfr_grade, 4)

    def test_egfr_drop(self):
        opts = dict(
            gender=MALE,
            age_in_years=25,
            ethnicity=BLACK,
            creatinine_value=10.15,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )
        egfr = Egfr(**opts)
        self.assertEqual(egfr.egfr_drop_value, 0.0)
        egfr = Egfr(baseline_egfr_value=23.0, **opts)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_value, 2), 7.33)
        self.assertEqual(egfr.egfr_grade, 4)
        self.assertEqual(egfr.egfr_grade, 4)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_drop_value, 2), 68.15)
        self.assertEqual(egfr.egfr_drop_grade, 4)
        self.assertEqual(egfr.egfr_drop_grade, 4)

    @override_settings(EDC_EGFR_DROP_NOTIFICATION_MODEL="egfr_app.EgfrDropNotification")
    def test_egfr_drop_with_notify(self):
        appointment = Appointment.objects.create(
            subject_identifier="1234",
            appt_datetime=get_utcnow(),
            timepoint=0,
        )
        subject_visit = SubjectVisit.objects.create(
            subject_identifier="1234",
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
        )

        panel = Panel.objects.get(name=rft_panel.name)

        requisition = SubjectRequisition.objects.create(
            subject_identifier="1234",
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime,
            panel=panel,
        )
        crf = ResultCrf.objects.create(
            subject_visit=subject_visit,
            requisition=requisition,
            report_datetime=appointment.appt_datetime,
            assay_datetime=appointment.appt_datetime,
            egfr_value=156.43,
            creatinine_value=53,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        opts = dict(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

        egfr = Egfr(
            baseline_egfr_value=220.1, percent_drop_threshold=20, calling_crf=crf, **opts
        )
        self.assertEqual(round_half_away_from_zero(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_drop_value, 2), 28.93)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertTrue(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        crf.creatinine_value = 48
        crf.save()
        crf.refresh_from_db()
        egfr = Egfr(
            baseline_egfr_value=220.1, percent_drop_threshold=20, calling_crf=crf, **opts
        )
        self.assertEqual(round_half_away_from_zero(egfr.egfr_value, 2), 162.93)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_drop_value, 2), 25.97)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertTrue(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        EgfrDropNotification.objects.all().delete()

        crf.creatinine_value = 53
        crf.save()
        crf.refresh_from_db()
        egfr = Egfr(
            baseline_egfr_value=190.1, percent_drop_threshold=20, calling_crf=crf, **opts
        )
        self.assertEqual(round_half_away_from_zero(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_drop_value, 2), 17.71)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertFalse(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        egfr = Egfr(
            baseline_egfr_value=100.1, percent_drop_threshold=20, calling_crf=crf, **opts
        )
        self.assertEqual(round_half_away_from_zero(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round_half_away_from_zero(egfr.egfr_drop_value, 2), 0.0)
        self.assertIsNone(egfr.egfr_drop_grade)
        self.assertFalse(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )
