from uuid import uuid4

from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import SiteModelMixin

from .product import Product


class Manager(models.Manager):
    use_in_migrations = True


class Stock(SiteModelMixin, BaseUuidModel):
    stock_identifier = models.CharField(max_length=36, default=uuid4, unique=True)

    product = models.ForeignKey(Product, on_delete=PROTECT)

    # TODO: location

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.stock_identifier}: {self.product} "

    class Meta(SiteModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Medication stock"
        verbose_name_plural = "Medication stock"
