from django import forms

from ..calculators import CalculatorError, eGFR
from ..convert_units import ConversionNotHandled


class EgfrFormValidatorMixin:
    def validate_egfr(self):
        if (
            self.cleaned_data.get("gender")
            and self.cleaned_data.get("age_in_years")
            and self.cleaned_data.get("ethnicity")
            and self.cleaned_data.get("creatinine_value")
            and self.cleaned_data.get("creatinine_units")
        ):
            opts = dict(
                gender=self.cleaned_data.get("gender"),
                age=self.cleaned_data.get("age_in_years"),
                ethnicity=self.cleaned_data.get("ethnicity"),
                creatinine_value=self.cleaned_data.get("creatinine_value"),
                creatinine_units=self.cleaned_data.get("creatinine_units"),
            )
            try:
                egfr = eGFR(**opts).value
            except (CalculatorError, ConversionNotHandled) as e:
                raise forms.ValidationError(e)
            return egfr
        return None
