from django import forms

from ..calculators import BMI, CalculatorError


class BmiFormValidatorMixin:
    def validate_bmi(self):
        if self.cleaned_data.get("height") and self.cleaned_data.get("weight"):
            try:
                bmi = BMI(
                    height_cm=self.cleaned_data.get("height"),
                    weight_kg=self.cleaned_data.get("weight"),
                ).value
            except CalculatorError as e:
                raise forms.ValidationError(e)
            return bmi
        return None
