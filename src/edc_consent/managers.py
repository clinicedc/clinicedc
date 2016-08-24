from django.db import models
from .site_consent_types import site_consent_types


class ObjectConsentManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):

    def valid_consent_for_period(self, subject_identifier, report_datetime):
        consent = None
        try:
            consent_type = site_consent_types.get_by_consent_datetime(
                self.model, report_datetime)
            if consent_type:
                consent = self.get(subject_identifier=subject_identifier, version=consent_type.version)
        except self.model.DoesNotExist:
            pass
        return consent
