from clinicedc_constants.choices import YES_NO
from django.db import models


class RequisitionVerifyModelMixin(models.Model):
    clinic_verified = models.CharField(max_length=15, choices=YES_NO, default="")

    clinic_verified_datetime = models.DateTimeField(null=True)

    class Meta:
        abstract = True
