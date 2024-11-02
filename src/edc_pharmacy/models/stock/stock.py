from decimal import Decimal

from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import InsufficientStockError
from ..storage import Location
from .container import Container
from .product import Product
from .receive_item import ReceiveItem


class Manager(models.Manager):
    use_in_migrations = True


class Stock(BaseUuidModel):

    stock_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    stock_datetime = models.DateTimeField(default=get_utcnow)

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    qty_in = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=20, default=Decimal(0.0)
    )

    qty_out = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    unit_qty_in = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    unit_qty_out = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal(0.0))

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock", related_name="source_stock", on_delete=models.PROTECT, null=True
    )

    description = models.CharField(max_length=100, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.stock_identifier}:{self.description}"

    def save(self, *args, **kwargs):
        if not self.stock_identifier:
            self.stock_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.receive_item:
                self.product = self.receive_item.order_item.product
            else:
                self.product = self.from_stock.receive_item.order_item.product  # noqa
        if not self.description:
            self.description = f"{self.product.name} - {self.container.name}"
        if self.qty_out > self.qty_in:
            raise InsufficientStockError("QTY OUT cannot exceed QTY IN.")
        if self.unit_qty_out > self.unit_qty_in:
            raise InsufficientStockError("Unit QTY OUT cannot exceed Unit QTY IN.")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
