from django.db import models
from edc_constants.constants import NEW
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ...choices import ORDER_CHOICES
from ...exceptions import InvalidContainer, OrderItemError
from .container import Container
from .order import Order
from .product import Product


class Manager(models.Manager):
    use_in_migrations = True


class OrderItem(BaseUuidModel):

    order_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=False)

    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=False)

    container = models.ForeignKey(
        Container,
        on_delete=models.PROTECT,
        limit_choices_to={"may_order_as": True},
        null=True,
        blank=False,
    )

    qty = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=20)

    unit_qty_ordered = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    unit_qty = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        null=True,
        help_text="unit qty ordered less unit qty received",
    )

    unit_qty_received = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    status = models.CharField(
        max_length=25, choices=ORDER_CHOICES, default=NEW, help_text="Updates in the signal"
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.order_item_identifier}:{self.product.name} | {self.container.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.order_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            self.unit_qty_ordered = self.qty * self.container.qty
            self.unit_qty = self.qty * self.container.qty
        if not self.order:
            raise OrderItemError("Order may not be null.")
        if not self.product:
            raise OrderItemError("Product may not be null.")
        if not self.container:
            raise OrderItemError("Container may not be null.")
        if not self.container.may_order_as:
            raise InvalidContainer(
                "Invalid container. Container is not configured for ordering. "
                f"Got {self.container}.Perhaps catch this in the form."
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Order item"
        verbose_name_plural = "Order items"
