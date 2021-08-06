from django import forms
from edc_reportable import CalculatorError, calculate_bmi


class WeightHeightBmiFormValidatorMixin:
    @staticmethod
    def validate_weight_height_with_bmi(weight_kg=None, height_cm=None, **kwargs):
        try:
            bmi = calculate_bmi(weight_kg=weight_kg, height_cm=height_cm, **kwargs)
        except CalculatorError as e:
            raise forms.ValidationError(f"Please check weight and height. {e}")
        return bmi
