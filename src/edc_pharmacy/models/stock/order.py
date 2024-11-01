from django.db import models
from edc_constants.constants import NEW
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from edc_pharmacy.choices import ORDER_CHOICES


class Manager(models.Manager):
    use_in_migrations = True


class Order(BaseUuidModel):

    order_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    order_datetime = models.DateTimeField(verbose_name="Order date/time")

    item_count = models.IntegerField(verbose_name="Item count", null=True)

    unit_qty = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    container_qty = models.DecimalField(
        null=True, blank=False, decimal_places=2, max_digits=10
    )

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
        verbose_name = "Stock: Order"
        verbose_name_plural = "Stock: Orders"
