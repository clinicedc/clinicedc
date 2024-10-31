from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords

from .container import Container
from .order_item import OrderItem
from .receive import Receive


class Manager(models.Manager):
    use_in_migrations = True


class ReceiveItem(BaseUuidModel):

    receive = models.ForeignKey(Receive, on_delete=models.PROTECT)

    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)

    container = models.ForeignKey(Container, on_delete=models.PROTECT)

    unit_qty = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    container_qty = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=10,
        help_text="qty of items in the containers (sum)",
    )

    added_to_stock = models.BooleanField(default=False)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.order_item

    def save(self, *args, **kwargs):
        if self.container.container_qty > 1:
            self.container_qty = self.unit_qty * self.container.container_qty
        else:
            self.container_qty = self.unit_qty
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock: Receive item"
        verbose_name_plural = "Stock: Receive items"
