from typing import Optional

from django import forms
from edc_constants.constants import NO
from edc_form_validators import FormValidator


class OgttFormValidatorMixin:
    def validate_ogtt_required_fields(self: FormValidator, ogtt_prefix: Optional[str] = None):
        """Uses fields `fasting`, `ogtt_base_datetime`, `ogtt_datetime`,
        `ogtt_value`, `ogtt_units`
        """
        ogtt_prefix = ogtt_prefix or "ogtt"
        self.required_if_true(
            self.cleaned_data.get(f"{ogtt_prefix}_datetime"),
            field_required=f"{ogtt_prefix}_value",
            inverse=False,
        )

        self.required_if_true(
            self.cleaned_data.get(f"{ogtt_prefix}_value"),
            field_required=f"{ogtt_prefix}_datetime",
            inverse=False,
        )

        self.not_required_if(
            NO,
            field="fasting",
            field_not_required=f"{ogtt_prefix}_base_datetime",
            inverse=False,
        )
        self.not_required_if(
            NO, field="fasting", field_not_required=f"{ogtt_prefix}_datetime", inverse=False
        )
        self.not_required_if(
            NO, field="fasting", field_not_required=f"{ogtt_prefix}_value", inverse=False
        )

        self.required_if_true(
            self.cleaned_data.get(f"{ogtt_prefix}_value"),
            field_required=f"{ogtt_prefix}_units",
        )

        self.not_required_if(
            NO, field="fasting", field_not_required=f"{ogtt_prefix}_units", inverse=False
        )

    def validate_ogtt_dates(self: FormValidator, ogtt_prefix: Optional[str] = None):
        ogtt_prefix = ogtt_prefix or "ogtt"
        ogtt_base_dte = self.cleaned_data.get(f"{ogtt_prefix}_base_datetime")
        ogtt_dte = self.cleaned_data.get(f"{ogtt_prefix}_datetime")
        if ogtt_base_dte and ogtt_dte:
            tdelta = ogtt_dte - ogtt_base_dte
            if tdelta.total_seconds() < 3600:
                raise forms.ValidationError(
                    {
                        f"{ogtt_prefix}_datetime": (
                            "Invalid. Expected more time between OGTT initial and 2hr."
                        )
                    }
                )
            if tdelta.seconds > (3600 * 5):
                raise forms.ValidationError(
                    {
                        f"{ogtt_prefix}_datetime": (
                            "Invalid. Expected less time between OGTT initial and 2hr."
                        )
                    }
                )

    def validate_ogtt_time_interval(self: FormValidator, ogtt_prefix: Optional[str] = None):
        """Validate the OGTT is measured 2 hrs after base date"""
        ogtt_prefix = ogtt_prefix or "ogtt"
        ogtt_base_dte = self.cleaned_data.get(f"{ogtt_prefix}_base_datetime")
        ogtt_dte = self.cleaned_data.get(f"{ogtt_prefix}_datetime")
        if ogtt_base_dte and ogtt_dte:
            diff = (ogtt_dte - ogtt_base_dte).total_seconds() / 60.0
            if diff <= 1.0:
                raise forms.ValidationError(
                    {
                        f"{ogtt_prefix}_datetime": (
                            "Invalid date. Expected to be after time oral glucose "
                            f"tolerance test was performed. ({diff})"
                        )
                    }
                )
