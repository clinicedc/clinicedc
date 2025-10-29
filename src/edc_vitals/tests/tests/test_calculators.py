from clinicedc_constants import BLACK, MALE
from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase, tag
from django.utils import timezone

from edc_form_validators import FormValidator
from edc_utils.round_up import round_half_away_from_zero
from edc_vitals.calculators import BMI, CalculatorError, calculate_bmi
from edc_vitals.form_validators import BmiFormValidatorMixin


@tag("vitals")
class TestCalculators(TestCase):
    def test_bmi_calculator(self):
        dob = timezone.now() - relativedelta(years=25)
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
                    report_datetime=timezone.now(),
                )
                try:
                    bmi = func(
                        weight_kg=56,
                        height_cm=150,
                        dob=dob,
                        report_datetime=timezone.now(),
                    )
                except CalculatorError as e:
                    self.fail(f"CalculatorError unexpectedly raises. Got {e}")
                else:
                    self.assertEqual(round_half_away_from_zero(bmi.value, 2), 24.89)

    @tag("1")
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
            dob=timezone.now() - relativedelta(years=30),
            report_datetime=timezone.now(),
        )
        form_validator = BmiFormValidator(cleaned_data=data)
        bmi = form_validator.validate_bmi()
        self.assertEqual(bmi.value, 24.8889)

        # calculation error
        data.update(
            weight=56,
            height=1.5,
            dob=timezone.now() - relativedelta(years=25),
            report_datetime=timezone.now(),
        )
        form_validator = BmiFormValidator(cleaned_data=data)
        self.assertRaises(forms.ValidationError, form_validator.validate_bmi)
