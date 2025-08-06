from django.db import models
from edc_constants.constants import NEW
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ...choices import ORDER_CHOICES
from .supplier import Supplier


class Manager(models.Manager):
    use_in_migrations = True


class Order(BaseUuidModel):

    order_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    order_datetime = models.DateTimeField(verbose_name="Order date/time")

    item_count = models.IntegerField(verbose_name="Item count", null=True)

    title = models.CharField(
        max_length=50, null=True, blank=False, help_text="A short description of this order"
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, verbose_name="Supplier", null=True, blank=False
    )
    comment = models.TextField(null=True, blank=True)

    sent = models.BooleanField(default=False)

    status = models.CharField(
        max_length=25, choices=ORDER_CHOICES, default=NEW, help_text="Updates in the signal"
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.order_identifier}"

    def save(self, *args, **kwargs):
        if not self.order_identifier:
            self.order_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Order"
        verbose_name_plural = "Orders"
