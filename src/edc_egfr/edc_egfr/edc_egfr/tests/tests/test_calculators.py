from django import forms
from django.test import TestCase
from edc_constants.constants import BLACK, FEMALE, MALE, NON_BLACK
from edc_form_validators import FormValidator
from edc_reportable import convert_units
from edc_reportable.units import (
    GRAMS_PER_DECILITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
)

from ... import EgfrCockcroftGault
from ...calculators import EgfrCalculatorError, EgfrCkdEpi, egfr_percent_change
from ...form_validator_mixins import (
    EgfrCkdEpiFormValidatorMixin,
    EgfrCockcroftGaultFormValidatorMixin,
)


class TestCalculators(TestCase):
    def test_creatinine_units(self):
        """U.S. units: 0.84 to 1.21 milligrams per deciliter (mg/dL);
        European units: 74.3 to 107 micromoles per liter (umol/L)
        """
        self.assertEqual(
            round(
                convert_units(
                    float(0.84),
                    units_from=MILLIGRAMS_PER_DECILITER,
                    units_to=MICROMOLES_PER_LITER,
                ),
                1,
            ),
            74.3,
        )
        self.assertEqual(
            round(
                convert_units(
                    float(1.21),
                    units_from=MILLIGRAMS_PER_DECILITER,
                    units_to=MICROMOLES_PER_LITER,
                ),
                1,
            ),
            107.0,
        )
        self.assertEqual(
            round(
                convert_units(
                    float(74.3),
                    units_from=MICROMOLES_PER_LITER,
                    units_to=MILLIGRAMS_PER_DECILITER,
                ),
                2,
            ),
            0.84,
        )
        self.assertEqual(
            round(
                convert_units(
                    float(107.0),
                    units_from=MICROMOLES_PER_LITER,
                    units_to=MILLIGRAMS_PER_DECILITER,
                ),
                2,
            ),
            1.21,
        )

    def test_egfr_ckd_epi_calculator(self):

        # raises on invalid gender
        self.assertRaises(
            EgfrCalculatorError,
            EgfrCkdEpi,
            gender="blah",
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
        )

        # raises on low age
        self.assertRaises(
            EgfrCalculatorError,
            EgfrCkdEpi,
            gender=FEMALE,
            age_in_years=3,
            creatinine_value=1.0,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
        )

        egfr = EgfrCkdEpi(
            gender=FEMALE,
            age_in_years=30,
        )
        self.assertRaises(EgfrCalculatorError, getattr, egfr, "value")

        egfr = EgfrCkdEpi(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=52.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(0.7, egfr.kappa)

        egfr = EgfrCkdEpi(
            gender=MALE,
            age_in_years=30,
            creatinine_value=52.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(0.9, egfr.kappa)

        egfr = EgfrCkdEpi(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=53.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(-0.329, egfr.alpha)

        egfr = EgfrCkdEpi(
            gender=MALE,
            age_in_years=30,
            creatinine_value=53.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(-0.411, egfr.alpha)

        egfr1 = EgfrCkdEpi(
            gender=MALE,
            ethnicity=BLACK,
            creatinine_value=53.0,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(round(egfr1.value, 2), 156.43)

        egfr2 = EgfrCkdEpi(
            gender=FEMALE,
            ethnicity=BLACK,
            creatinine_value=53.0,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(round(egfr2.value, 2), 141.81)

        egfr1 = EgfrCkdEpi(
            gender=MALE,
            ethnicity=NON_BLACK,
            creatinine_value=53.0,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(round(egfr1.value, 2), 134.97)

        egfr2 = EgfrCkdEpi(
            gender=FEMALE,
            ethnicity=NON_BLACK,
            creatinine_value=53.0,
            age_in_years=30,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertEqual(round(egfr2.value, 2), 122.35)

    def test_egfr_cockcroft_gault_calculator(self):

        # raises on invalid gender
        self.assertRaises(
            EgfrCalculatorError,
            EgfrCockcroftGault,
            gender="blah",
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        # raises on low age
        self.assertRaises(
            EgfrCalculatorError,
            EgfrCockcroftGault,
            gender=FEMALE,
            age_in_years=3,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
            weight=65.0,
        )

        # raises on missing weight
        egfr = EgfrCockcroftGault(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=1.0,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.assertRaises(EgfrCalculatorError, getattr, egfr, "value")

        egfr = EgfrCockcroftGault(
            gender=MALE,
            age_in_years=30,
            creatinine_value=50.0,
            creatinine_units=MICROMOLES_PER_LITER,
            weight=65.0,
        )
        self.assertEqual(round(egfr.value, 2), 175.89)

        egfr = EgfrCockcroftGault(
            gender=MALE,
            age_in_years=30,
            creatinine_value=50.8,
            creatinine_units=MICROMOLES_PER_LITER,
            weight=65.0,
        )
        self.assertEqual(round(egfr.value, 2), 173.12)

        egfr = EgfrCockcroftGault(
            gender=MALE,
            age_in_years=30,
            creatinine_value=50.9,
            creatinine_units=MICROMOLES_PER_LITER,
            weight=65.0,
        )
        self.assertEqual(round(egfr.value, 2), 172.78)

        egfr = EgfrCockcroftGault(
            gender=FEMALE,
            age_in_years=30,
            creatinine_value=50.9,
            creatinine_units=MICROMOLES_PER_LITER,
            weight=65.0,
        )
        self.assertEqual(round(egfr.value, 2), 147.5)

        egfr = EgfrCockcroftGault(
            gender=FEMALE,
            creatinine_value=1.3,
            age_in_years=30,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            weight=65.0,
        )

        self.assertEqual(round(egfr.value, 2), 65.31)

        egfr2 = EgfrCockcroftGault(
            gender=MALE,
            creatinine_value=0.9,
            age_in_years=30,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            weight=65.0,
        )

        self.assertEqual(round(egfr2.value, 2), 110.51)

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
        self.assertEqual(round(egfr, 2), 718.14)

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

    def test_egfr_percent_change(self):
        self.assertGreater(egfr_percent_change(51.10, 131.50), 20.0)
        self.assertLess(egfr_percent_change(51.10, 61.10), 20.0)
        self.assertEqual(egfr_percent_change(51.10, 51.10), 0.0)
        self.assertLess(egfr_percent_change(51.10, 21.10), 20.0)
        self.assertEqual(egfr_percent_change(51.10, 0), 0.0)
