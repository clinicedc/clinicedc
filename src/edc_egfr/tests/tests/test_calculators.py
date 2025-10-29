from clinicedc_constants import (
    BLACK,
    MALE,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
)
from django import forms
from django.test import TestCase, tag

from edc_egfr.form_validator_mixins import (
    EgfrCkdEpiFormValidatorMixin,
    EgfrCockcroftGaultFormValidatorMixin,
)
from edc_form_validators import FormValidator
from edc_utils.round_up import round_half_away_from_zero


@tag("egfr")
class TestCalculators(TestCase):
    def test_egfr_ckd_epi_2009_form_validator(self):
        data = dict(gender=MALE, ethnicity=BLACK, age_in_years=30)

        class EgfrFormValidator(EgfrCkdEpiFormValidatorMixin, FormValidator):
            calculator_version = 2009

            def validate_egfr(self) -> float | None:
                return super().validate_egfr(
                    gender=self.cleaned_data.get("gender"),
                    age_in_years=self.cleaned_data.get("age_in_years"),
                    ethnicity=self.cleaned_data.get("ethnicity"),
                )

        # not enough data
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

        # calculates
        data.update(creatinine_value=53.0, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round_half_away_from_zero(egfr, 2), 156.42)

        # calculation error: bad units
        data.update(creatinine_units="blah")
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

    def test_egfr_ckd_epi_2021_form_validator(self):
        data = dict(gender=MALE, age_in_years=30)

        class EgfrFormValidator(EgfrCkdEpiFormValidatorMixin, FormValidator):
            calculator_version = 2021

            def validate_egfr(self) -> float | None:
                return super().validate_egfr(
                    gender=self.cleaned_data.get("gender"),
                    age_in_years=self.cleaned_data.get("age_in_years"),
                )

        # calculates
        data.update(creatinine_value=53.0, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round_half_away_from_zero(egfr, 2), 130.03)

    def test_egfr_cockcroft_gault_form_validator(self):
        data = dict(
            gender=MALE,
            weight=72,
            age_in_years=30,
        )

        class EgfrFormValidator(EgfrCockcroftGaultFormValidatorMixin, FormValidator):
            calculator_version = 2009

            def validate_egfr(self) -> float | None:
                return super().validate_egfr(
                    gender=self.cleaned_data.get("gender"),
                    age_in_years=self.cleaned_data.get("age_in_years"),
                    weight_in_kgs=self.cleaned_data.get("weight"),
                )

        # not enough data
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

        # calculation error: bad units
        data.update(creatinine_value=1.3, creatinine_units="blah")
        form_validator = EgfrFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_egfr)

        # calculates
        data.update(creatinine_value=1.30, creatinine_units=MILLIGRAMS_PER_DECILITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round_half_away_from_zero(egfr, 2), 84.77)

        # calculates
        data.update(creatinine_value=114.94, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = EgfrFormValidator(cleaned_data=data)
        egfr = form_validator.validate_egfr()
        self.assertEqual(round_half_away_from_zero(egfr, 2), 84.75)
