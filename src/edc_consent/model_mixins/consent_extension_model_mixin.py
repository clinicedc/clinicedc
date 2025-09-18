from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django_crypto_fields.fields import EncryptedTextField

from edc_constants.choices import YES_NO_NA
from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin

from .. import site_consents
from ..consent_definition_extension import ConsentDefinitionExtension
from ..exceptions import ConsentExtensionDefinitionModelError

___all__ = ["ConsentExtensionModelMixin"]


class ConsentExtensionModelMixin(UniqueSubjectIdentifierModelMixin, models.Model):
    # declare with an FK your subject consent!
    subject_consent = models.ForeignKey("mysubjectconsent", on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=timezone.now)

    agrees_to_extension = models.CharField(
        verbose_name=_(
            "Does the participant give consent to extend clinic "
            "followup as per the protocol amendment?"
        ),
        max_length=15,
        choices=YES_NO_NA,
        help_text=_("See above for the definition of extended followup."),
    )

    comment = EncryptedTextField(verbose_name="Comment", max_length=250, blank=True, null=True)

    consent_extension_version = models.CharField(
        verbose_name="Consent extension version",
        max_length=10,
        default="",
        editable=False,
    )

    consent_extension_definition_name = models.CharField(
        verbose_name="Consent extension definition",
        max_length=50,
        default="",
        editable=False,
    )

    def __str__(self) -> str:
        if self.subject_identifier:
            return f"{self._meta.verbose_name} for {self.subject_identifier}"
        return ""

    def save(self, *args, **kwargs):
        self.subject_identifier = self.subject_consent.subject_identifier
        cdefext = self.consent_definition_extension
        self.consent_extension_version = cdefext.version
        self.consent_extension_definition_name = cdefext.name
        super().save(*args, **kwargs)

    @property
    def consent_definition_extension(self) -> ConsentDefinitionExtension:
        cdef = site_consents.get_consent_definition(
            model=self.subject_consent._meta.label_lower,
            version=self.subject_consent.version,
            report_datetime=self.report_datetime,
        )
        if self._meta.label_lower != cdef.extended_by.model:
            raise ConsentExtensionDefinitionModelError(
                f"Incorrect model for consent definition extension. "
                f"This model cannot be used "
                f"to 'extend' consent version '{cdef.version}'. Expected "
                f"'{cdef.extended_by.model}'. Got '{self._meta.label_lower}'."
            )
        return cdef.extended_by

    class Meta:
        abstract = True
