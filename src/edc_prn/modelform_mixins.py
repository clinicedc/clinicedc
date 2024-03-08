from __future__ import annotations

from datetime import datetime

from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_crf.crf_form_validator_mixins import BaseFormValidatorMixin


class PrnFormValidatorMixin(BaseFormValidatorMixin):
    """to be declared with PRN FormValidators."""

    report_datetime_field_attr = "report_datetime"

    @property
    def subject_consent(self):
        return self.get_consent_definition(
            report_datetime=self.report_datetime
        ).model_cls.objects.get(subject_identifier=self.subject_identifier)

    def get_consent_definition(
        self, report_datetime: datetime = None, fldname: str = None, error_code: str = None
    ) -> ConsentDefinition:
        return site_consents.get_consent_definition(report_datetime=self.report_datetime)

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
