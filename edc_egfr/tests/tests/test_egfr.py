from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_constants.constants import BLACK, MALE
from edc_reportable import (
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    site_reportables,
)
from edc_reportable.grading_data.daids_july_2017 import grading_data
from edc_reportable.normal_data.africa import normal_data
from edc_utils import get_utcnow

from edc_egfr.calculators import EgfrCalculatorError
from edc_egfr.egfr import Egfr, EgfrError
from egfr_app.models import Appointment, EgfrDropNotification, ResultCrf, SubjectVisit


class TestEgfr(TestCase):
    def setUp(self) -> None:
        site_reportables._registry = {}

        site_reportables.register(
            name="my_reference_list", normal_data=normal_data, grading_data=grading_data
        )

    def test_ok(self):
        egfr = Egfr(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=52,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            calculator_name="ckd-epi",
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

    def test_egfr_grade(self):
        egfr = Egfr(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=275,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            calculator_name="ckd-epi",
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
            calculator_name="ckd-epi",
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
            calculator_name="ckd-epi",
        )
        egfr = Egfr(**opts)
        self.assertEqual(egfr.egfr_drop_value, 0.0)
        egfr = Egfr(baseline_egfr_value=23.0, **opts)
        self.assertEqual(round(egfr.egfr_value, 2), 7.33)
        self.assertEqual(egfr.egfr_grade, 4)
        self.assertEqual(egfr.egfr_grade, 4)
        self.assertEqual(round(egfr.egfr_drop_value, 2), 68.15)
        self.assertEqual(egfr.egfr_drop_grade, 4)
        self.assertEqual(egfr.egfr_drop_grade, 4)

    @override_settings(EDC_EGFR_DROP_NOTIFICATION_MODEL="egfr_app.EgfrDropNotification")
    def test_egfr_drop_with_notify(self):
        appointment = Appointment.objects.create(
            subject_identifier="1234",
            appt_datetime=get_utcnow(),
        )
        subject_visit = SubjectVisit.objects.create(
            subject_identifier="1234",
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
        )

        crf = ResultCrf.objects.create(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime,
            assay_datetime=appointment.appt_datetime,
            egfr_value=156.43,
        )
        opts = dict(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            creatinine_value=53,
            creatinine_units=MICROMOLES_PER_LITER,
            report_datetime=get_utcnow(),
            reference_range_collection_name="my_reference_list",
            calculator_name="ckd-epi",
        )

        egfr = Egfr(
            baseline_egfr_value=220.1, notify_on_percent_drop=20, calling_crf=crf, **opts
        )
        self.assertEqual(round(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round(egfr.egfr_drop_value, 2), 28.93)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertTrue(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        opts.update(creatinine_value=48)
        egfr = Egfr(
            baseline_egfr_value=220.1, notify_on_percent_drop=20, calling_crf=crf, **opts
        )
        self.assertEqual(round(egfr.egfr_value, 2), 162.93)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round(egfr.egfr_drop_value, 2), 25.97)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertTrue(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        EgfrDropNotification.objects.filter(subject_visit=subject_visit).delete()

        opts.update(creatinine_value=53)
        egfr = Egfr(
            baseline_egfr_value=190.1, notify_on_percent_drop=20, calling_crf=crf, **opts
        )
        self.assertEqual(round(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round(egfr.egfr_drop_value, 2), 17.71)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertEqual(egfr.egfr_drop_grade, 2)
        self.assertFalse(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )

        egfr = Egfr(
            baseline_egfr_value=100.1, notify_on_percent_drop=20, calling_crf=crf, **opts
        )
        self.assertEqual(round(egfr.egfr_value, 2), 156.43)
        self.assertIsNone(egfr.egfr_grade)
        self.assertEqual(round(egfr.egfr_drop_value, 2), 0.0)
        self.assertIsNone(egfr.egfr_drop_grade)
        self.assertFalse(
            EgfrDropNotification.objects.filter(subject_visit=subject_visit).exists()
        )
