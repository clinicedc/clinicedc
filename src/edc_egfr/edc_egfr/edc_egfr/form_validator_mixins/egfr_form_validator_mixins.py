from typing import Any

from django import forms
from edc_reportable import CalculatorError, ConversionNotHandled

from ..calculators import EgfrCkdEpi, EgfrCockcroftGault


class EgfrCkdEpiFormValidatorMixin:
    def validate_egfr(self: Any):
        if (
            self.cleaned_data.get("gender")
            and self.cleaned_data.get("age_in_years")
            and self.cleaned_data.get("ethnicity")
            and self.cleaned_data.get("creatinine_value")
            and self.cleaned_data.get("creatinine_units")
        ):
            opts = dict(
                gender=self.cleaned_data.get("gender"),
                age_in_years=self.cleaned_data.get("age_in_years"),
                ethnicity=self.cleaned_data.get("ethnicity"),
                creatinine_value=self.cleaned_data.get("creatinine_value"),
                creatinine_units=self.cleaned_data.get("creatinine_units"),
            )
            try:
                egfr = EgfrCkdEpi(**opts).value
            except (CalculatorError, ConversionNotHandled) as e:
                raise forms.ValidationError(e)
            return egfr
        return None


class EgfrCockcroftGaultFormValidatorMixin:
    def validate_egfr(self: Any):
        if (
            self.cleaned_data.get("gender")
            and self.cleaned_data.get("age_in_years")
            and self.cleaned_data.get("weight")
            and self.cleaned_data.get("creatinine_value")
            and self.cleaned_data.get("creatinine_units")
        ):
            opts = dict(
                gender=self.cleaned_data.get("gender"),
                age_in_years=self.cleaned_data.get("age_in_years"),
                weight=self.cleaned_data.get("weight"),
                creatinine_value=self.cleaned_data.get("creatinine_value"),
                creatinine_units=self.cleaned_data.get("creatinine_units"),
            )
            try:
                egfr = EgfrCockcroftGault(**opts).value
            except (CalculatorError, ConversionNotHandled) as e:
                raise forms.ValidationError(e)
            return egfr
        return None
