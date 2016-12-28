from django.db import models

from .site_consents import site_consents


class ObjectConsentManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):

    def first_consent(self, subject_identifier):
        consents = self.filter(subject_identifier=subject_identifier)
        try:
            return consents[0]
        except IndexError:
            return None

    def consent_for_period(self, subject_identifier, report_datetime):
        consent = site_consents.get_consent(
            consent_model=self.model._meta.label_lower,
            report_datetime=report_datetime)
        subject_consent = None
        try:
            if consent:
                subject_consent = self.get(subject_identifier=subject_identifier, version=consent.version)
        except self.model.DoesNotExist:
            subject_consent = None
        return subject_consent
