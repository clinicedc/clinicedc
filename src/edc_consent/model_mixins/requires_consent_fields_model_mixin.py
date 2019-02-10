from django.db import models


class RequiresConsentFieldsModelMixin(models.Model):

    consent_model = models.CharField(max_length=50, null=True, editable=False)

    consent_version = models.CharField(max_length=10, null=True, editable=False)

    class Meta:
        abstract = True
