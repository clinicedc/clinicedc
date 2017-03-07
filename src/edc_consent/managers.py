from django.db import models

from .site_consents import site_consents
from .exceptions import ConsentDoesNotExist


class ObjectConsentManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):

    def first_consent(self, subject_identifier):
        """Returns the first consent in the sytem for this subject_identifier
        by consent_datetime."""
        return self.filter(subject_identifier=subject_identifier).order_by(
            'consent_datetime').first()

    def consent_for_period(self, subject_identifier, report_datetime):
        """Returns a consent model instance or None."""
        subject_consent = None
        try:
            consent = site_consents.get_consent(
                consent_model=self.model._meta.label_lower,
                consent_group=self.model._meta.consent_group,
                report_datetime=report_datetime)
        except ConsentDoesNotExist:
            pass
        else:
            try:
                subject_consent = self.get(
                    subject_identifier=subject_identifier, version=consent.version)
            except self.model.DoesNotExist:
                pass
        return subject_consent
