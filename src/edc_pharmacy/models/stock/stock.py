import uuid

from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import InsufficientStockError
from ..storage import Location
from .container import Container
from .product import Product
from .receive_item import ReceiveItem


class Manager(models.Manager):
    use_in_migrations = True


class Stock(BaseUuidModel):

    stock_identifier = models.CharField(max_length=25, unique=True)

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    unit_qty_in = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=10, default=1
    )

    unit_qty_out = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)

    container_qty = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=10
    )

    container_qty_in = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=10
    )

    container_qty_out = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock", related_name="source_stock", on_delete=models.PROTECT, null=True
    )

    description = models.CharField(max_length=100, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self.id:
            self.stock_identifier = str(uuid.uuid4())
            self.product = self.receive_item.order_item.product
        if not self.description:
            self.description = (
                f"{self.receive_item.order_item.product.name} - {self.container.name}"
            )
        if float(self.container_qty_out) > float(self.container_qty_in):
            raise InsufficientStockError("Container QTY cannot be less than zero.")
        self.container_qty = float(self.container_qty_in) - float(self.container_qty_out)
        if self.container_qty_in == self.container_qty_out:
            self.qty_out = 1
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication: Stock"
        verbose_name_plural = "Medication: Stock"
