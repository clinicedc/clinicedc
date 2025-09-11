from __future__ import annotations

from datetime import datetime

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

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
        self,
        report_datetime: datetime = None,
        fldname: str = None,
        error_code: str = None,
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


class PrnSingletonModelFormMixin:
    def clean(self) -> dict:
        cleaned_data = super().clean()
        self.raise_if_singleton_exists()
        return cleaned_data

    def raise_if_singleton_exists(self) -> None:
        """Raise if singleton model instance exists."""
        if not self.instance.id:
            opts = {"subject_identifier": (self.get_subject_identifier())}
            try:
                self._meta.model.objects.get(**opts)
            except ObjectDoesNotExist:
                pass
            else:
                msg_string = _("Invalid. This form has already been submitted.")
                error_msg = format_lazy("{msg_string}", msg_string=msg_string)
                raise forms.ValidationError(error_msg)
