from django.db import models

from ..requires_consent import RequiresConsent


class RequiresConsentFieldsMixin(models.Model):

    """Requires a model to check for and set a valid
    consent version before allowing to save.

    Requires attrs subject_identfier, schedule, report_datetime.
    """

    requires_consent_cls = RequiresConsent

    consent_model = models.CharField(
        max_length=50,
        editable=False)

    consent_version = models.CharField(
        max_length=10,
        editable=False)

    class Meta:
        abstract = True
