from django import forms

from ..calculators import CalculatorError, calculate_bmi

__all__ = ["BmiFormValidatorMixin"]


class BmiFormValidatorMixin:
    def validate_bmi(self, **kwargs):
        try:
            bmi = calculate_bmi(
                height_cm=self.cleaned_data.get("height"),
                weight_kg=self.cleaned_data.get("weight"),
                **self.cleaned_data,
                **kwargs,
            )
        except CalculatorError as e:
            raise forms.ValidationError(str(e)) from e
        return bmi
