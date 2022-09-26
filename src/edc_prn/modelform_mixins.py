from __future__ import annotations

from datetime import datetime

from edc_crf.form_validator_mixins import BaseFormValidatorMixin
from edc_utils import to_utc


class PrnFormValidatorMixin(BaseFormValidatorMixin):
    @property
    def subject_identifier(self) -> str | None:
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        else:
            subject_identifier = getattr(self.instance, "subject_identifier", None)
        return subject_identifier

    @property
    def report_datetime(self) -> datetime | None:
        """Returns the report_datetime in UTC from cleaned_data,
        if key exists, else returns the instance report_datetime.
        """
        if self.report_datetime_field_attr in self.cleaned_data:
            return to_utc(self.cleaned_data.get(self.report_datetime_field_attr))
        else:
            return getattr(self.instance, self.report_datetime_field_attr)
