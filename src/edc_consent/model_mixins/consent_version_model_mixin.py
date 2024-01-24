from django.db import models, transaction
from edc_sites import site_sites

from edc_consent import site_consents
from edc_consent.exceptions import SiteConsentError


class ConsentVersionModelMixin(models.Model):
    """A model mixin that adds version to a consent.

    Requires at least `NonUniqueSubjectIdentifierModelMixin` (or
    `UniqueSubjectIdentifierModelMixin`), `SiteModelMixin` and
    the field `consent_datetime`.
    """

    version = models.CharField(
        verbose_name="Consent version",
        max_length=10,
        help_text="See 'Consent Type' for consent versions by period.",
        editable=False,
    )

    updates_versions = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_subject_identifier()} v{self.version}"

    def save(self, *args, **kwargs):
        consent_definition = self.get_consent_definition()
        self.version = consent_definition.version
        self.updates_versions = True if consent_definition.updates_versions else False
        if self.updates_versions:
            with transaction.atomic():
                consent_definition.get_previous_consent(
                    subject_identifier=self.get_subject_identifier(),
                    version=self.version,
                )
        super().save(*args, **kwargs)

    def get_consent_definition(self):
        """Allow the consent to save as long as there is a
        consent definition for this report_date and site.
        """
        site = self.site
        if not self.id and not site:
            site = site_sites.get_current_site_obj()
        consent_definition = site_consents.get_consent_definition(
            model=self._meta.label_lower,
            report_datetime=self.consent_datetime,
            site=site_sites.get(site.id),
        )
        if consent_definition.model != self._meta.label_lower:
            raise SiteConsentError(
                f"No consent definitions exist for this consent model. Got {self}."
            )
        return consent_definition

    class Meta:
        abstract = True
