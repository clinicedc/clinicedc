from dateutil.relativedelta import relativedelta
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_model import estimated_date_from_ago


class InitialReviewFormValidatorMixin:
    def dx_before_reference_date_or_raise(self: FormValidator, reference_date_fld: str):
        dx_date = self.cleaned_data.get("dx_date")
        if not dx_date and self.cleaned_data.get("dx_ago"):
            dx_date = estimated_date_from_ago(
                cleaned_data=self.cleaned_data, ago_field="dx_ago"
            )
        if dx_date and self.cleaned_data.get(reference_date_fld):
            est_med_start_dte = estimated_date_from_ago(
                cleaned_data=self.cleaned_data, ago_field=reference_date_fld
            )
            if (dx_date - est_med_start_dte).days > 1:
                self.raise_validation_error(
                    {reference_date_fld: "Invalid. Cannot be before diagnosis."}, INVALID_ERROR
                )

    def validate_test_date_within_6m(self: FormValidator, date_fld: str):
        if self.cleaned_data.get(date_fld) and self.cleaned_data.get("report_datetime"):
            rdelta = relativedelta(
                self.cleaned_data.get("report_datetime"),
                self.cleaned_data.get(date_fld),
            )
            months = rdelta.months + (12 * rdelta.years)
            if months >= 6 or months < 0:
                if months < 0:
                    msg = "Invalid. Cannot be a future date."
                else:
                    msg = f"Invalid. Must be within the last 6 months. Got {abs(months)}m ago."
                self.raise_validation_error(
                    {date_fld: msg},
                    INVALID_ERROR,
                )
