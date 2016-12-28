from django import forms
from django.core.exceptions import ObjectDoesNotExist

from ..site_consents import site_consents


class RequiresConsentModelFormMixin:

    def clean(self):
        cleaned_data = super().clean()
        self.validate_against_consent()
        return cleaned_data

    def validate_against_consent(self):
        """Raise an exception if the report datetime doesn't make sense relative to the consent."""
        cleaned_data = self.cleaned_data
        appointment = cleaned_data.get('appointment')
        consent = self.get_consent(appointment.subject_identifier, cleaned_data.get("report_datetime"))
        if cleaned_data.get("report_datetime") < consent.consent_datetime:
            raise forms.ValidationError("Report datetime cannot be before consent datetime")
        if cleaned_data.get("report_datetime").date() < consent.dob:
            raise forms.ValidationError("Report datetime cannot be before DOB")

    def get_consent(self, subject_identifier, report_datetime):
        """Return an instance of the consent model."""
        consent_config = site_consents.get_consent_by_datetime(
            report_datetime=report_datetime,
            consent_model=self._meta.model._meta.consent_model)
        try:
            consent = consent_config.model.objects.get(
                subject_identifier=subject_identifier)
        except consent_config.model.MultipleObjectsReturned:
            consent = consent_config.model.objects.filter(
                subject_identifier=subject_identifier).order_by('version').first()
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                '\'{}\' does not exist for subject.'.format(consent_config.model._meta.verbose_name))
        return consent
