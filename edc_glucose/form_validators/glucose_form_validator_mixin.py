from __future__ import annotations

from dateutil.relativedelta import relativedelta
from edc_constants.constants import YES

from ..utils import validate_glucose_as_millimoles_per_liter

INVALID_GLUCOSE_DATE = "INVALID_GLUCOSE_DATE"


class GlucoseFormValidatorMixin:
    prefix: str | None = None

    def validate_glucose_test(self, prefix: str | None = None) -> None:
        prefix = prefix or self.prefix or "glucose"
        self.applicable_if(
            YES, field=f"{prefix}_performed", field_applicable=f"{prefix}_fasting"
        )
        self.required_if(
            YES, field=f"{prefix}_fasting", field_required=f"{prefix}_fasting_duration_str"
        )
        self.required_if(YES, field=f"{prefix}_performed", field_required=f"{prefix}_date")
        self.required_if(YES, field=f"{prefix}_performed", field_required=f"{prefix}_value")
        validate_glucose_as_millimoles_per_liter(prefix, self.cleaned_data)
        self.required_if(
            YES, field=f"{prefix}_performed", field_required=f"{prefix}_quantifier"
        )
        self.required_if(YES, field=f"{prefix}_performed", field_required=f"{prefix}_units")

    def validate_test_date_within_max_months(
        self, date_fld: str, max_months: int | None = None
    ):
        max_months = max_months or 6
        if self.cleaned_data.get(date_fld) and self.cleaned_data.get("report_datetime"):
            try:
                dt = self.cleaned_data.get(date_fld).date()
            except AttributeError:
                dt = self.cleaned_data.get(date_fld)
            report_datetime = self.cleaned_data.get("report_datetime").date()
            rdelta = relativedelta(report_datetime, dt)
            months = rdelta.months + (12 * rdelta.years)
            if months >= max_months or months < 0:
                if months < 0:
                    msg = "Invalid. Cannot be a future date."
                else:
                    msg = (
                        f"Invalid. Must be within the last {max_months} months. "
                        f"Got {abs(months)}m ago."
                    )
                self.raise_validation_error({date_fld: msg}, INVALID_GLUCOSE_DATE)
