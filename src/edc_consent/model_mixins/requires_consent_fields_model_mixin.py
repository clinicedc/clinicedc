from django.db import models


class RequiresConsentFieldsModelMixin(models.Model):
    """See pre-save signal that checks if subject is consented"""

    consent_model = models.CharField(max_length=50, default="", blank=True)

    consent_version = models.CharField(max_length=10, default="", blank=True)

    class Meta:
        abstract = True
