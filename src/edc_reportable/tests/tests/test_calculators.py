from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_constants.constants import BLACK, FEMALE, MALE
from edc_form_validators import FormValidator
from edc_utils import get_utcnow

from edc_reportable import (
    GRAMS_PER_DECILITER,
    BmiFormValidatorMixin,
    EgfrCkdEpiFormValidatorMixin,
    EgfrCockcroftGaultFormValidatorMixin,
    calculate_bmi,
)
from edc_reportable.units import MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER

from ...calculators import BMI, CalculatorError, EgfrCkdEpi


class TestCalculators(TestCase):
    def test_bmi_calculator(self):
        dob = get_utcnow() - relativedelta(years=25)
        self.assertRaises(CalculatorError, BMI, weight_kg=56, height_cm=None)
        try:
            calculate_bmi(weight_kg=56, height_cm=None, dob=dob)
        except CalculatorError:
            self.fail("CalculatorError unexpectedly raised ")

        for func in [BMI, calculate_bmi]:
            with self.subTest(func=func):
                self.assertRaises(
                    CalculatorError,
                    func,
                    weight_kg=56,
                    height_cm=1.50,
                    dob=dob,
                    report_datetime=get_utcnow(),
                )
                try:
                    bmi = func(
                        weight_kg=56, height_cm=150, dob=dob, report_datetime=get_utcnow()
                    )
                except CalculatorError as e:
                    self.fail(f"CalculatorError unexpectedly raises. Got {e}")
                else:
                    self.assertEqual(round(bmi.value, 2), 24.89)

    def test_egfr_ckd_epi_calculator(self):

        # raises on invalid gender
        self.assertRaises(
            CalculatorError,
            EgfrCkdEpi,
            gender="blah",
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        # raises on low age
        self.assertRaises(
            CalculatorError,
            EgfrCkdEpi,
            gender=FEMALE,
            age_in_years=3,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        egfr = EgfrCkdEpi(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(0.7, egfr.kappa)

        egfr = EgfrCkdEpi(
            gender=MALE,
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(0.9, egfr.kappa)

        egfr = EgfrCkdEpi(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(-0.329, egfr.alpha)

        egfr = EgfrCkdEpi(
            gender=MALE,
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(-0.411, egfr.alpha)

        egfr1 = EgfrCkdEpi(
            gender=MALE,
            ethnicity=BLACK,
            creatinine_value=1.3,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        self.assertEqual(round(egfr1.value, 2), 712.56)

        egfr2 = EgfrCkdEpi(
            gender=MALE,
            ethnicity=BLACK,
            creatinine_value=0.9,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        self.assertEqual(round(egfr2.value, 2), 828.04)

    def test_bmi_form_validator(self):
        data = dict(
            gender=MALE,
            ethnicity=BLACK,
            age_in_years=30,
        )

        class BmiFormValidator(BmiFormValidatorMixin, FormValidator):
            pass

        # not enough data
        form_validator = BmiFormValidator(cleaned_data=data)
        bmi = form_validator.validate_bmi()
        self.assertIsNone(bmi)

        # calculates
        data.update(
            weight=56,
            height=150,
            dob=get_utcnow() - relativedelta(years=30),
            report_datetime=get_utcnow(),
        )
        form_validator = BmiFormValidator(cleaned_data=data)
        bmi = form_validator.validate_bmi()
        self.assertEqual(bmi.value, 24.8889)

        # calculation error
        data.update(
            weight=56,
            height=1.5,
            dob=get_utcnow() - relativedelta(years=25),
            report_datetime=get_utcnow(),
        )
        form_validator = BmiFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_bmi)

    def test_egfr_ckd_epi_form_validator(self):
        data = dict(
            gender=MALE,
            ethnicity=BLACK,
            age_in_years=30,
        )

        class EgfrFormValidator(EgfrCkdEpiFormValidatorMixin, FormValidator):
            pass

        # not enough data
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertIsNone(egfr)

        # calculates
        data.update(creatinine_value=1.3, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round(egfr, 2), 712.56)

        # calculation error: bad units
        data.update(creatinine_units=GRAMS_PER_DECILITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

    def test_egfr_cockcroft_gault_form_validator(self):
        data = dict(
            gender=MALE,
            weight=72,
            age_in_years=30,
        )

        class EgfrFormValidator(EgfrCockcroftGaultFormValidatorMixin, FormValidator):
            pass

        # not enough data
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertIsNone(egfr)

        # calculation error: bad units
        data.update(creatinine_value=1.3, creatinine_units=GRAMS_PER_DECILITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

        # calculates
        data.update(creatinine_value=1.30, creatinine_units=MILLIGRAMS_PER_DECILITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round(egfr, 2), 84.75)

        # calculates
        data.update(creatinine_value=114.94, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round(egfr, 2), 84.75)
