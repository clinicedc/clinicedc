from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .site_consents import SiteConsentError, site_consents


class ObjectConsentManager(models.Manager):
    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):
    def first_consent(self, subject_identifier=None):
        """Returns the first consent by consent_datetime."""
        return (
            self.filter(subject_identifier=subject_identifier)
            .order_by("consent_datetime")
            .first()
        )

    def consent_for_period(self, subject_identifier=None, report_datetime=None):
        """Returns a consent model instance or None."""
        model_obj = None
        try:
            consent_object = site_consents.get_consent_for_period(
                model=self.model._meta.label_lower,
                consent_group=self.model._meta.consent_group,
                report_datetime=report_datetime,
            )
        except SiteConsentError:
            pass
        else:
            try:
                model_obj = self.get(
                    subject_identifier=subject_identifier,
                    version=consent_object.version,
                )
            except ObjectDoesNotExist:
                pass
        return model_obj
