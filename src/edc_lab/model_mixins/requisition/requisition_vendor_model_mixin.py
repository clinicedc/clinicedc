from clinicedc_constants import NULL_STRING
from django.db import models


class RequisitionVendorModelMixin(models.Model):
    resulted = models.BooleanField(default=False)

    laboratory_id = models.CharField(null=NULL_STRING, blank=True, max_length=25)

    order_number = models.CharField(null=NULL_STRING, blank=True, max_length=50)

    order_datetime = models.DateTimeField(null=True, blank=True)

    result_number = models.CharField(null=NULL_STRING, blank=True, max_length=50)

    result_datetime = models.DateTimeField(null=True, blank=True)

    specimen_number = models.CharField(null=NULL_STRING, blank=True, max_length=50)

    specimen_received_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
