from django.db import models
from django.db.models import PROTECT
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords

from .product import Product


class Manager(models.Manager):
    use_in_migrations = True


class Order(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    order_datetime = models.DateTimeField(verbose_name="Order date/time")

    product = models.ForeignKey(Product, on_delete=PROTECT)

    qty_ordered = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    qty_supplied = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    objects = Manager()

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication order"
        verbose_name_plural = "Medication orders"
