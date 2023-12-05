from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from .product import Product


class Manager(models.Manager):
    use_in_migrations = True


class StockReceiving(BaseUuidModel):
    product = models.ForeignKey(Product, on_delete=PROTECT)

    qty = models.IntegerField()

    stock_identifiers = models.TextField()

    received = models.BooleanField(default=False)

    received_datetime = models.DateTimeField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.product}: {self.qty} recv'd on {self.received_datetime}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication stock: Receiving"
        verbose_name_plural = "Medication stock: Receiving"
