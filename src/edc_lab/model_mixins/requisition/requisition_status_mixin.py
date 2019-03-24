from django.db import models


class RequisitionStatusMixin(models.Model):

    received = models.BooleanField(default=False)

    received_datetime = models.DateTimeField(null=True, blank=True)

    processed = models.BooleanField(default=False)

    processed_datetime = models.DateTimeField(null=True, blank=True)

    packed = models.BooleanField(default=False)

    packed_datetime = models.DateTimeField(null=True, blank=True)

    shipped = models.BooleanField(default=False)

    shipped_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
