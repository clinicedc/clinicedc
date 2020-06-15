from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_tracking.modelform_mixins import get_subject_visit

from ..constants import DEFAULT_CONSENT_GROUP
from ..site_consents import site_consents


class RequiresConsentModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        self.validate_against_consent()
        return cleaned_data

    @property
    def report_datetime(self):
        """Returns the report_datetime from directly from
        cleaned_data or via the subject_visit.
        """
        report_datetime = self.cleaned_data.get("report_datetime")
        subject_visit = get_subject_visit(
            self, subject_visit_attr=self._meta.model.visit_model_attr()
        )
        if subject_visit and not report_datetime:
            report_datetime = subject_visit.report_datetime
        return report_datetime

    def validate_against_consent(self):
        """Raise an exception if the report datetime doesn't make
        sense relative to the consent.
        """
        try:
            subject_identifier = self.cleaned_data["appointment"].subject_identifier
        except KeyError:
            subject_visit = get_subject_visit(
                self, subject_visit_attr=self._meta.model.visit_model_attr()
            )
            subject_identifier = subject_visit.appointment.subject_identifier
        consent = self.get_consent(subject_identifier, self.report_datetime)
        if self.report_datetime < consent.consent_datetime:
            raise forms.ValidationError(
                "Report datetime cannot be before consent datetime"
            )
        if self.report_datetime.date() < consent.dob:
            raise forms.ValidationError("Report datetime cannot be before DOB")

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
        consent_object = site_consents.get_consent(
            report_datetime=report_datetime,
            consent_group=self.consent_group,
            model=self.consent_model,
        )
        try:
            obj = consent_object.model_cls.consent.consent_for_period(
                subject_identifier=subject_identifier, report_datetime=report_datetime
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f"`{consent_object.model_cls._meta.verbose_name}` does not exist "
                f"to cover this subject on {report_datetime.strftime('Y%-%m-%d %Z')}"
            )
        return obj
