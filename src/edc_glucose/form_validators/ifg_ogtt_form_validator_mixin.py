from django import forms

from ..utils import validate_glucose_as_millimoles_per_liter
from .ifg_form_validator_mixin import IfgFormValidatorMixin
from .ogtt_form_validator_mixin import OgttFormValidatorMixin


class IfgOgttFormValidatorMixin(IfgFormValidatorMixin, OgttFormValidatorMixin):
    def validate_glucose_testing_matrix(self):
        self.validate_ifg_required_fields()
        validate_glucose_as_millimoles_per_liter("ifg", self.cleaned_data)
        self.validate_ogtt_required_fields()
        validate_glucose_as_millimoles_per_liter("ogtt", self.cleaned_data)
        self.validate_ogtt_dates()
        self.validate_ifg_before_ogtt()
        self.validate_ogtt_time_interval()

    def validate_ifg_before_ogtt(self):
        """Validate the IFG is performed before the OGTT"""
        ifg_dte = self.cleaned_data.get("ifg_datetime")
        ogtt_base_dte = self.cleaned_data.get("ogtt_base_datetime")
        if ifg_dte and ogtt_base_dte:
            total_seconds = (ogtt_base_dte - ifg_dte).total_seconds()
            if total_seconds <= 1:
                raise forms.ValidationError(
                    {
                        "ogtt_base_datetime": (
                            "Invalid date. Expected to be after time " "IFG level was measured"
                        )
                    }
                )
