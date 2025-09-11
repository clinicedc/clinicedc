from __future__ import annotations

from django import forms
from edc_constants.constants import NO


class OgttFormValidatorMixin:
    def validate_ogtt_required_fields(
        self,
        ogtt_prefix: str | None = None,
        fasting_prefix: str | None = None,
    ) -> None:
        """Uses fields `fasting`, `ogtt_base_datetime`, `ogtt_datetime`,
        `ogtt_value`, `ogtt_units`
        """
        ogtt = ogtt_prefix or "ogtt"
        fasting = fasting_prefix or "fasting"
        self.required_if_true(
            self.cleaned_data.get(f"{ogtt}_datetime"),
            field_required=f"{ogtt}_value",
            inverse=False,
        )

        self.required_if_true(
            self.cleaned_data.get(f"{ogtt}_value"),
            field_required=f"{ogtt}_datetime",
            inverse=False,
        )

        self.not_required_if(
            NO,
            field=fasting,
            field_not_required=f"{ogtt}_base_datetime",
            inverse=False,
        )
        self.not_required_if(
            NO, field=fasting, field_not_required=f"{ogtt}_datetime", inverse=False
        )
        self.not_required_if(
            NO, field=fasting, field_not_required=f"{ogtt}_value", inverse=False
        )

        self.required_if_true(
            self.cleaned_data.get(f"{ogtt}_value"),
            field_required=f"{ogtt}_units",
        )

        self.not_required_if(
            NO, field=fasting, field_not_required=f"{ogtt}_units", inverse=False
        )

    def validate_ogtt_dates(self, ogtt_prefix: str | None = None) -> None:
        ogtt = ogtt_prefix or "ogtt"
        ogtt_base_dte = self.cleaned_data.get(f"{ogtt}_base_datetime")
        ogtt_dte = self.cleaned_data.get(f"{ogtt}_datetime")
        if ogtt_base_dte and ogtt_dte:
            tdelta = ogtt_dte - ogtt_base_dte
            if tdelta.total_seconds() < 3600:
                raise forms.ValidationError(
                    {
                        f"{ogtt}_datetime": (
                            "Invalid. Expected more time between OGTT initial and 2hr."
                        )
                    }
                )
            if tdelta.seconds > (3600 * 5):
                raise forms.ValidationError(
                    {
                        f"{ogtt}_datetime": (
                            "Invalid. Expected less time between OGTT initial and 2hr."
                        )
                    }
                )

    def validate_ogtt_time_interval(self, ogtt_prefix: str | None = None) -> None:
        """Validate the OGTT is measured 2 hrs after base date"""
        ogtt = ogtt_prefix or "ogtt"
        ogtt_base_dte = self.cleaned_data.get(f"{ogtt}_base_datetime")
        ogtt_dte = self.cleaned_data.get(f"{ogtt}_datetime")
        if ogtt_base_dte and ogtt_dte:
            diff = (ogtt_dte - ogtt_base_dte).total_seconds() / 60.0
            if diff <= 1.0:
                raise forms.ValidationError(
                    {
                        f"{ogtt}_datetime": (
                            "Invalid date. Expected to be after time oral glucose "
                            f"tolerance test was performed. ({diff})"
                        )
                    }
                )
