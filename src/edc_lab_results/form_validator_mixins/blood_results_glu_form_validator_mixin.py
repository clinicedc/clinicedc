from typing import Any

from edc_glucose.utils import validate_glucose_as_millimoles_per_liter

from .blood_results_fbg_form_validator_mixin import BloodResultsFbgFormValidatorMixin


class BloodResultsGluFormValidatorMixin(BloodResultsFbgFormValidatorMixin):
    def evaluate_value(self: Any, field_name: str):
        if field_name == "glucose_value":
            validate_glucose_as_millimoles_per_liter("glucose", self.cleaned_data)
