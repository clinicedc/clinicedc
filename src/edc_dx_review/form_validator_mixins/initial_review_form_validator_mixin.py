from __future__ import annotations

from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_model import estimated_date_from_ago


class InitialReviewFormValidatorMixin(FormValidator):
    dx_date_fld: str = "dx_date"
    dx_ago_fld: str = "dx_ago"

    def __init__(self, **kwargs):
        self._dx_date: date | datetime | None = None
        super().__init__(**kwargs)

    @property
    def dx_date(self) -> datetime | date | None:
        if not self._dx_date:
            fld = None
            self.raise_if_both_dx_ago_and_dx_date()
            if self.cleaned_data.get(self.dx_date_fld):
                self._dx_date = self.cleaned_data.get(self.dx_date_fld)
                fld = self.dx_date_fld
            elif self.cleaned_data.get(self.dx_ago_fld):
                self._dx_date = estimated_date_from_ago(
                    cleaned_data=self.cleaned_data, ago_field=self.dx_ago_fld
                )
                fld = self.dx_ago_fld
            self.raise_if_dx_date_is_future(self._dx_date, field=fld)
        return self._dx_date

    @property
    def dx_ago(self) -> str | None:
        return self.cleaned_data.get(self.dx_ago_fld)

    def raise_if_both_dx_ago_and_dx_date(self):
        if self.cleaned_data.get(self.dx_date_fld) and self.cleaned_data.get(self.dx_ago_fld):
            self.raise_validation_error(
                {
                    self.dx_ago_fld: (
                        "Date conflict. Do not provide a response "
                        "here if the date of diagnosis is available."
                    )
                },
                INVALID_ERROR,
            )

    def raise_if_dx_date_is_future(self, dx_date: date | None, field: str | None):
        if dx_date:
            self.date_is_past(
                field=field,
                field_value=dx_date,
                reference_field="report_datetime",
            )

    # def dx_before_reference_date_or_raise(
    #     self: FormValidator, reference_date_fld: str, msg: str | None = None
    # ):
    #     dx_date = self.cleaned_data.get("dx_date")
    #     msg = msg or "Invalid. Cannot be before diagnosis."
    #     if not dx_date and self.cleaned_data.get("dx_ago"):
    #         dx_date = estimated_date_from_ago(
    #             cleaned_data=self.cleaned_data, ago_field="dx_ago"
    #         )
    #     if dx_date and self.cleaned_data.get(reference_date_fld):
    #         est_med_start_dte = estimated_date_from_ago(
    #             cleaned_data=self.cleaned_data, ago_field=reference_date_fld
    #         )
    #         if (dx_date - est_med_start_dte).days > 1:
    #             self.raise_validation_error({reference_date_fld: msg}, INVALID_ERROR)

    def validate_test_date_within_6m(self: FormValidator, date_fld: str):
        if self.cleaned_data.get(date_fld) and self.cleaned_data.get("report_datetime"):
            try:
                dt = self.cleaned_data.get(date_fld).date()
            except AttributeError:
                dt = self.cleaned_data.get(date_fld)
            report_datetime = self.cleaned_data.get("report_datetime").date()
            rdelta = relativedelta(report_datetime, dt)
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
