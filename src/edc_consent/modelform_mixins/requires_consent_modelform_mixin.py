from django import forms
from django.conf import settings

from ..constants import DEFAULT_CONSENT_GROUP
from ..site_consents import site_consents


class RequiresConsentModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        self.validate_against_consent()
        return cleaned_data

    def validate_against_consent(self):
        """Raise an exception if the report datetime doesn't make
        sense relative to the consent.
        """
        cleaned_data = self.cleaned_data
        consent = self.get_consent(
            self.appointment.subject_identifier, cleaned_data.get("report_datetime")
        )
        if cleaned_data.get("report_datetime") < consent.consent_datetime:
            raise forms.ValidationError(
                "Report datetime cannot be before consent datetime"
            )
        if cleaned_data.get("report_datetime").date() < consent.dob:
            raise forms.ValidationError("Report datetime cannot be before DOB")

    @property
    def appointment(self):
        return self.cleaned_data.get("appointment")

    @property
    def consent_group(self):
        try:
            consent_group = self._meta.model._meta.consent_group
        except AttributeError:
            consent_group = DEFAULT_CONSENT_GROUP
        return consent_group

    @property
    def consent_model(self):
        try:
            consent_model = self._meta.model._meta.consent_model
        except AttributeError:
            consent_model = settings.SUBJECT_CONSENT_MODEL
        return consent_model

    def get_consent(self, subject_identifier, report_datetime):
        """Return an instance of the consent model.
        """
        consent = site_consents.get_consent(
            report_datetime=report_datetime,
            consent_group=self.consent_group,
            model=self.consent_model,
        )
        try:
            obj = consent.model.consent.consent_for_period(
                subject_identifier=subject_identifier, report_datetime=report_datetime
            )
        except consent.model.DoesNotExist:
            raise forms.ValidationError(
                "'{}' does not exist to cover this subject on {}.".format(
                    consent.model._meta.verbose_name,
                    report_datetime=report_datetime.strftime("Y%-%m-%d %Z"),
                )
            )
        return obj
