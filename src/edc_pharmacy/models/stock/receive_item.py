from decimal import Decimal

from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import InvalidContainer
from .container import Container
from .order_item import OrderItem
from .receive import Receive


class Manager(models.Manager):
    use_in_migrations = True


class ReceiveItem(BaseUuidModel):

    receive_item_identifier = models.CharField(
        max_length=36, unique=True, null=True, blank=True
    )

    receive = models.ForeignKey(
        Receive,
        on_delete=models.PROTECT,
        blank=False,
    )

    receive_item_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(
        max_length=200, null=True, blank=True, help_text="Leave blank to use default"
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        blank=False,
    )

    container = models.ForeignKey(
        Container,
        on_delete=models.PROTECT,
        limit_choices_to={"may_receive_as": True},
        blank=False,
    )

    qty = models.DecimalField(
        verbose_name="Quantity", null=True, blank=False, decimal_places=2, max_digits=20
    )

    unit_qty = models.DecimalField(
        verbose_name="Unit quantity",
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=20,
        help_text="Quantity x Container.Quantity, e.g. 10 x Bottle of 128 = 1280",
    )

    added_to_stock = models.BooleanField(default=False)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.receive_item_identifier}:"
            f"{self.order_item.product.name}"
            f" | {self.container.name}"
        )

    def save(self, *args, **kwargs):
        if not self.receive_item_identifier:
            self.receive_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if self.container.qty > Decimal(1.0):
            self.unit_qty = self.qty * self.container.qty
        else:
            self.unit_qty = self.qty
        if not self.name:
            self.name = f"{self.order_item.product.name} | {self.container.name}"
        if not self.container.may_receive_as:
            raise InvalidContainer(
                "Invalid container. Container is not configured for receiving. "
                f"Got {self.container}"
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock: Receive item"
        verbose_name_plural = "Stock: Receive items"
