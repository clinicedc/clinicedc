from django.test import TestCase, tag
from edc_constants.constants import FEMALE, MALE, BLACK

from ...calculators import eGFR, CalculatorError, BMI
from edc_reportable.units import MICROMOLES_PER_LITER


class TestCalculators(TestCase):
    def test_bmi_calculator(self):

        bmi = BMI(weight_kg=56, height_cm=1.50)
        self.assertRaises(CalculatorError, getattr, bmi, "value")

        bmi = BMI(weight_kg=56, height_cm=150)
        try:
            bmi.value
        except CalculatorError as e:
            self.fail(f"CalculatorError unexpectedly raises. Got {e}")
        else:
            self.assertEqual(round(bmi.value, 2), 24.89)

    def test_egfr_calculator(self):

        egfr = eGFR(
            gender=FEMALE, age=30, creatinine=1.0, creatinine_units=MICROMOLES_PER_LITER
        )
        self.assertEqual(0.7, egfr.kappa)

        egfr = eGFR(
            gender=MALE, age=30, creatinine=1.0, creatinine_units=MICROMOLES_PER_LITER
        )
        self.assertEqual(0.9, egfr.kappa)

        egfr = eGFR(
            gender=FEMALE, age=30, creatinine=1.0, creatinine_units=MICROMOLES_PER_LITER
        )
        self.assertEqual(-0.329, egfr.alpha)

        egfr = eGFR(
            gender=MALE, age=30, creatinine=1.0, creatinine_units=MICROMOLES_PER_LITER
        )
        self.assertEqual(-0.411, egfr.alpha)

        egfr1 = eGFR(
            gender=MALE,
            ethnicity=BLACK,
            creatinine=1.3,
            age=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        self.assertEquals(round(egfr1.value, 2), 712.56)

        egfr2 = eGFR(
            gender=MALE,
            ethnicity=BLACK,
            creatinine=0.9,
            age=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )

        self.assertEquals(round(egfr2.value, 2), 828.04)
