from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from ..storage import Location
from .product_unit import ProductUnit
from .receive_item import ReceiveItem


class Manager(models.Manager):
    use_in_migrations = True


class Material(BaseUuidModel):

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)

    qty_in = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    converted_qty_in = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=10
    )

    converted_qty_out = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=10
    )

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    description = models.CharField(max_length=100, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = (
                f"{self.receive_item.order_item.product.name} - {self.product_unit.name}"
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication: Stock"
        verbose_name_plural = "Medication: Stock"
