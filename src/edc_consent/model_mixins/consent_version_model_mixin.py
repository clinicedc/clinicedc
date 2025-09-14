from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

from edc_consent import site_consents
from edc_consent.exceptions import ConsentDefinitionModelError
from edc_sites import site_sites


class ConsentVersionModelMixin(models.Model):
    """A model mixin that adds version to a consent.

    Requires at least `NonUniqueSubjectIdentifierModelMixin` (or
    `UniqueSubjectIdentifierModelMixin`), `SiteModelMixin` and
    the field `consent_datetime`.
    """

    version = models.CharField(
        verbose_name="Consent version",
        max_length=10,
        help_text="See 'consent definition' for consent versions by period.",
        editable=False,
    )

    update_versions = models.BooleanField(default=False)

    consent_definition_name = models.CharField(
        verbose_name="Consent definition", max_length=50, null=True, editable=False
    )

    def __str__(self):
        return f"{self.get_subject_identifier()} v{self.version}"

    def save(self, *args, **kwargs):
        cdef = self.consent_definition
        self.version = cdef.version
        self.consent_definition_name = cdef.name
        if not self.id and self.subject_identifier:
            try:
                with transaction.atomic():
                    previous_consent = cdef.get_previous_consent(
                        subject_identifier=self.subject_identifier, exclude_id=self.id
                    )
            except ObjectDoesNotExist:
                pass
            else:
                self.first_name = previous_consent.first_name
                self.dob = previous_consent.dob
                self.initials = previous_consent.initials
                self.identity = previous_consent.identity
                self.confirm_identity = previous_consent.confirm_identity
        super().save(*args, **kwargs)

    @property
    def consent_definition(self):
        """Allow the consent to save as long as there is a
        consent definition for this report_date and site.
        """
        site = self.site
        if not self.id and not site:
            site = site_sites.get_current_site_obj()
        cdef = site_consents.get_consent_definition(
            model=self._meta.label_lower,
            report_datetime=self.consent_datetime,
            site=site_sites.get(site.id),
        )
        if self._meta.label_lower != cdef.model:
            raise ConsentDefinitionModelError(
                f"Incorrect model for consent_definition. This model cannot be used "
                f"to 'create' consent version '{cdef.version}'. Expected "
                f"'{cdef.model}'. Got '{self._meta.label_lower}'."
            )
        if cdef.updates and self._meta.label_lower != cdef.updates.updated_by.model:
            raise ConsentDefinitionModelError(
                f"Incorrect model to update a consent. This model cannot be used "
                f"to 'update' consent version '{cdef.version}'. Expected "
                f"'{cdef.updates.updated_by.model}'. Got '{self._meta.label_lower}'."
            )
        return cdef

    class Meta:
        abstract = True
