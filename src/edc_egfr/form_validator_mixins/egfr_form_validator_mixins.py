from clinicedc_utils import (
    ConversionNotHandled,
    EgfrCalculatorError,
    EgfrCkdEpi2009,
    EgfrCkdEpi2021,
    EgfrCockcroftGault,
)
from django import forms

from edc_form_validators import INVALID_ERROR


class EgfrCkdEpiFormValidatorMixin:
    calculator_version = 2009

    @property
    def egfr_calculator_cls(self) -> type[EgfrCkdEpi2009 | EgfrCkdEpi2021]:
        if self.calculator_version == 2009:  # noqa: PLR2004
            cls = EgfrCkdEpi2009
        elif self.calculator_version == 2021:  # noqa: PLR2004
            cls = EgfrCkdEpi2021
        else:
            raise EgfrCalculatorError(
                f"Invalid calculator version. Got {self.calculator_version}."
            )
        return cls

    def validate_egfr(
        self, *, gender: str, age_in_years: int, ethnicity: str | None = None
    ) -> float | None:
        opts = dict(
            gender=gender,
            age_in_years=age_in_years,
            creatinine_value=self.cleaned_data.get("creatinine_value"),
            creatinine_units=self.cleaned_data.get("creatinine_units"),
        )
        if self.egfr_calculator_cls == EgfrCkdEpi2009:
            opts.update(ethnicity=ethnicity)
        try:
            value = self.egfr_calculator_cls(**opts).value
        except (EgfrCalculatorError, ConversionNotHandled) as e:
            raise forms.ValidationError(e) from e
        return value


class EgfrCockcroftGaultFormValidatorMixin:
    def validate_egfr(
        self, *, gender: str, age_in_years: int, weight_in_kgs: float
    ) -> float | None:
        opts = dict(
            gender=gender,
            age_in_years=age_in_years,
            weight=weight_in_kgs,
            creatinine_value=self.cleaned_data.get("creatinine_value"),
            creatinine_units=self.cleaned_data.get("creatinine_units"),
        )
        try:
            value = EgfrCockcroftGault(**opts).value
        except (EgfrCalculatorError, ConversionNotHandled) as e:
            self.raise_validation_error({"__all__": str(e)}, INVALID_ERROR, exc=e)
        return value
