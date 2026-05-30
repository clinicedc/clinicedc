from clinicedc_constants import NOT_EVALUATED
from clinicedc_constants.choices import YES_NO_NOT_EVALUATED
from django.db import models


class RequisitionVerifyModelMixin(models.Model):
    clinic_verified = models.CharField(
        max_length=15,
        choices=YES_NO_NOT_EVALUATED,
        default=NOT_EVALUATED,
    )

    clinic_verified_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
