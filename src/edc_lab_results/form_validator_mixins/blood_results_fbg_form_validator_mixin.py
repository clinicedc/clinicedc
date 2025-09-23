from typing import Any

from django import forms

from edc_constants.constants import FASTING, YES
from edc_glucose.utils import validate_glucose_as_millimoles_per_liter


class BloodResultsFbgFormValidatorMixin:
    @property
    def reportables_evaluator_options(self: Any):
        if not self.cleaned_data.get("fasting"):
            raise forms.ValidationError({"fasting": "This field is required."})
        fasting = bool(
            self.cleaned_data.get("fasting") == FASTING
            or self.cleaned_data.get("fasting") == YES
        )
        return dict(fasting=fasting)

    def evaluate_value(self, prefix: str = None):
        validate_glucose_as_millimoles_per_liter(prefix=prefix, cleaned_data=self.cleaned_data)
