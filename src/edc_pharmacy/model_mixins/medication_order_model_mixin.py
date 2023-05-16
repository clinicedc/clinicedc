from django.db import models
from django.db.models import PROTECT


class MedicationOrderModelMixin(models.Model):
    stock = models.ForeignKey(
        "edc_pharmacy.stock",
        null=True,
        blank=False,
        on_delete=PROTECT,
    )

    qty = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    packed = models.BooleanField(default=False)
    packed_datetime = models.DateTimeField(null=True, blank=True)

    shipped = models.BooleanField(default=False)
    shipped_datetime = models.DateTimeField(null=True, blank=True)

    received_at_site = models.BooleanField(default=False)
    received_at_site_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
