from __future__ import annotations

from datetime import datetime

from edc_crf.crf_form_validator_mixins import BaseFormValidatorMixin


class PrnFormValidatorMixin(BaseFormValidatorMixin):
    """to be declared with PRN FormValidators."""

    report_datetime_field_attr = "report_datetime"

    @property
    def report_datetime(self) -> datetime:
        """Returns report_datetime or raises.

        Report datetime is always a required field on a CRF model,
        Django will raise a field ValidationError before getting
        here if report_datetime is None.
        """
        report_datetime = None
        if self.report_datetime_field_attr in self.cleaned_data:
            report_datetime = self.cleaned_data.get(self.report_datetime_field_attr)
        elif self.instance:
            report_datetime = self.instance.report_datetime
        return report_datetime
