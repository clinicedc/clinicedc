from django.db import models


class RequiresConsentFieldsModelMixin(models.Model):
    """See pre-save signal that checks if subject is consented"""

    consent_model = models.CharField(max_length=50, null=True, blank=True)

    consent_version = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        abstract = True
