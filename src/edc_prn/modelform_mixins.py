from __future__ import annotations

from edc_crf.form_validator_mixins import BaseFormValidatorMixin
from edc_form_validators.form_validator_mixins import ReportDatetimeFormValidatorMixin


class PrnFormValidatorMixin(ReportDatetimeFormValidatorMixin, BaseFormValidatorMixin):
    @property
    def subject_identifier(self) -> str | None:
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        else:
            subject_identifier = getattr(self.instance, "subject_identifier", None)
        return subject_identifier
