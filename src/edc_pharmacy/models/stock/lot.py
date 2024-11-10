from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import LotError
from ..medication import Assignment
from .product import Product


class Manager(models.Manager):
    use_in_migrations = True


class Lot(BaseUuidModel):

    lot_no = models.CharField(max_length=50, unique=True)

    product = models.ForeignKey(Product, on_delete=PROTECT, null=True, blank=False)

    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, null=True, blank=True)

    expiration_date = models.DateField()

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.product} Lot {self.lot_no}"

    def save(self, *args, **kwargs):
        if self.assignment != self.product.assignment:
            raise LotError("Assignment mismatch.")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Lot"
        verbose_name_plural = "Lots"
