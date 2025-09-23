from django import forms

from edc_form_validators import INVALID_ERROR
from edc_reportable import ConversionNotHandled
from edc_vitals.calculators import CalculatorError

from ..calculators import EgfrCalculatorError, EgfrCkdEpi, EgfrCockcroftGault


class EgfrCkdEpiFormValidatorMixin:
    def validate_egfr(
        self,
        gender: str = None,
        age_in_years: int = None,
        weight_in_kgs: float = None,
        ethnicity: str = None,
        baseline_egfr_value: float | None = None,
    ):
        opts = dict(
            gender=gender,
            age_in_years=age_in_years,
            weight=weight_in_kgs,
            ethnicity=ethnicity,
            creatinine_value=self.cleaned_data.get("creatinine_value"),
            creatinine_units=self.cleaned_data.get("creatinine_units"),
            baseline_egfr_value=baseline_egfr_value,
        )
        try:
            value = EgfrCkdEpi(**opts).value
        except (EgfrCalculatorError, CalculatorError, ConversionNotHandled) as e:
            raise forms.ValidationError(e)
        return value


class EgfrCockcroftGaultFormValidatorMixin:
    def validate_egfr(
        self,
        *,
        gender: str,
        age_in_years: int,
        weight_in_kgs: float,
        ethnicity: str,
    ):
        opts = dict(
            gender=gender,
            age_in_years=age_in_years,
            weight=weight_in_kgs,
            ethnicity=ethnicity,
            creatinine_value=self.cleaned_data.get("creatinine_value"),
            creatinine_units=self.cleaned_data.get("creatinine_units"),
        )
        try:
            value = EgfrCockcroftGault(**opts).value
        except (EgfrCalculatorError, CalculatorError, ConversionNotHandled) as e:
            self.raise_validation_error({"__all__": str(e)}, INVALID_ERROR)
        return value
