from django.db import models
from edc_constants.choices import YES_NO


class RequisitionVerifyModelMixin(models.Model):

    clinic_verified = models.CharField(
        max_length=15,
        choices=YES_NO,
        null=True)

    clinic_verified_datetime = models.DateTimeField(null=True)

    class Meta:
        abstract = True
