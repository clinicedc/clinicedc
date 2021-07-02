from django import forms
from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator

from edc_glucose.utils import validate_glucose_as_millimoles_per_liter


class GlucoseFormValidatorMixin(FormValidator):
    def validate_glucose_test(self):
        self.required_if(YES, field="glucose_performed", field_required="glucose_date")
        self.required_if(YES, field="glucose_performed", field_required="fasting")
        self.required_if(YES, field="glucose_performed", field_required="glucose_value")
        validate_glucose_as_millimoles_per_liter("glucose", self.cleaned_data)
        self.required_if(YES, field="glucose_performed", field_required="glucose_quantifier")
        self.applicable_if(YES, field="glucose_performed", field_applicable="glucose_units")

    def validate_glucose_testing_matrix(self):
        self.validate_ifg_required_fields()
        validate_glucose_as_millimoles_per_liter("ifg", self.cleaned_data)
        self.validate_ogtt_required_fields()
        validate_glucose_as_millimoles_per_liter("ogtt", self.cleaned_data)
        self.validate_ogtt_dates()
        self.validate_ifg_before_ogtt()
        self.validate_ogtt_time_interval()

    def validate_ifg_required_fields(self):
        """Uses fields `fasting`,`fasting_duration_str`, `ifg_value`,
        `ifg_datetime`, `ifg_units`
        """
        self.required_if(YES, field="fasting", field_required="fasting_duration_str")

        self.required_if(YES, field="fasting", field_required="ifg_datetime")

        self.required_if(YES, field="fasting", field_required="ifg_value")

        self.required_if_true(
            self.cleaned_data.get("ifg_datetime"),
            field_required="ifg_value",
        )

        self.required_if_true(
            self.cleaned_data.get("ifg_value"),
            field_required="ifg_units",
        )

        self.required_if_true(
            self.cleaned_data.get("ifg_value"),
            field_required="ifg_datetime",
        )

    def validate_ogtt_required_fields(self):
        """Uses fields `fasting`, `ogtt_base_datetime`, `ogtt_datetime`,
        `ogtt_value`, `ogtt_units`
        """
        self.required_if_true(
            self.cleaned_data.get("ogtt_datetime"),
            field_required="ogtt_value",
            inverse=False,
        )

        self.required_if_true(
            self.cleaned_data.get("ogtt_value"),
            field_required="ogtt_datetime",
            inverse=False,
        )

        self.not_required_if(
            NO, field="fasting", field_not_required="ogtt_base_datetime", inverse=False
        )
        self.not_required_if(
            NO, field="fasting", field_not_required="ogtt_datetime", inverse=False
        )
        self.not_required_if(
            NO, field="fasting", field_not_required="ogtt_value", inverse=False
        )

        self.required_if_true(self.cleaned_data.get("ogtt_value"), field_required="ogtt_units")

        self.not_required_if(
            NO, field="fasting", field_not_required="ogtt_units", inverse=False
        )

    def validate_ogtt_dates(self):
        ogtt_base_dte = self.cleaned_data.get("ogtt_base_datetime")
        ogtt_dte = self.cleaned_data.get("ogtt_datetime")
        if ogtt_base_dte and ogtt_dte:
            dt1 = ogtt_base_dte.date()
            dt2 = ogtt_dte.date()
            if dt1.year != dt2.year or dt1.month != dt2.month or dt1.day != dt2.day:
                raise forms.ValidationError(
                    {
                        "ogtt_datetime": (
                            "Invalid date. Expected same day as OGTT initial date."
                        )
                    }
                )
            tdelta = ogtt_dte - ogtt_base_dte
            if tdelta.total_seconds() < 3600:
                raise forms.ValidationError(
                    {
                        "ogtt_datetime": (
                            "Invalid. Expected more time between OGTT initial and 2hr."
                        )
                    }
                )
            if tdelta.seconds > (3600 * 5):
                raise forms.ValidationError(
                    {
                        "ogtt_datetime": (
                            "Invalid. Expected less time between OGTT initial and 2hr."
                        )
                    }
                )

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

    def validate_ogtt_time_interval(self):
        """Validate the OGTT is measured 2 hrs after base date"""
        ogtt_base_dte = self.cleaned_data.get("ogtt_base_datetime")
        ogtt_dte = self.cleaned_data.get("ogtt_datetime")
        if ogtt_base_dte and ogtt_dte:
            diff = (ogtt_dte - ogtt_base_dte).total_seconds() / 60.0
            if diff <= 1.0:
                raise forms.ValidationError(
                    {
                        "ogtt_datetime": (
                            "Invalid date. Expected to be after time oral glucose "
                            f"tolerance test was performed. ({diff})"
                        )
                    }
                )
