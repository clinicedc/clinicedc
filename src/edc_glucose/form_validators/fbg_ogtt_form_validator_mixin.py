from typing import Optional

from django import forms

from ..utils import validate_glucose_as_millimoles_per_liter
from .fbg_form_validator_mixin import FbgFormValidatorMixin
from .ogtt_form_validator_mixin import OgttFormValidatorMixin


class FbgOgttFormValidatorMixin(FbgFormValidatorMixin, OgttFormValidatorMixin):
    def validate_glucose_testing_matrix(
        self,
        report_datetime_fld: str,
        ogtt_prefix: Optional[str] = None,
        fbg_prefix: Optional[str] = None,
        include_fbg=None,
    ):
        ogtt_prefix = ogtt_prefix or "ogtt"
        fbg_prefix = fbg_prefix or "fbg"

        include_fbg = True if include_fbg is None else include_fbg
        if include_fbg:
            self.validate_fbg_required_fields(fbg_prefix, report_datetime_fld)
            validate_glucose_as_millimoles_per_liter(fbg_prefix, self.cleaned_data)
        self.validate_ogtt_required_fields(ogtt_prefix=ogtt_prefix)
        validate_glucose_as_millimoles_per_liter(ogtt_prefix, self.cleaned_data)
        self.validate_ogtt_dates(ogtt_prefix=ogtt_prefix)
        self.validate_fbg_before_ogtt(ogtt_prefix=ogtt_prefix, fbg_prefix=fbg_prefix)
        self.validate_ogtt_time_interval()

    def validate_fbg_before_ogtt(
        self, ogtt_prefix: Optional[str] = None, fbg_prefix: Optional[str] = None
    ):
        """Validate the FBG is performed before the OGTT"""
        ogtt_prefix = ogtt_prefix or "ogtt"
        fbg_prefix = fbg_prefix or "fbg"
        fbg_dte = self.cleaned_data.get(f"{fbg_prefix}_datetime")
        ogtt_base_dte = self.cleaned_data.get(f"{ogtt_prefix}_base_datetime")
        if fbg_dte and ogtt_base_dte:
            total_seconds = (ogtt_base_dte - fbg_dte).total_seconds()
            if total_seconds <= 1:
                raise forms.ValidationError(
                    {
                        f"{ogtt_prefix}_base_datetime": (
                            "Invalid date. Expected to be after time FBG level was measured"
                        )
                    }
                )
