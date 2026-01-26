from decimal import Decimal

from clinicedc_constants import NULL_STRING
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ...exceptions import InvalidContainer, ReceiveError, ReceiveItemError
from .container import Container
from .lot import Lot
from .order_item import OrderItem
from .receive import Receive


class Manager(models.Manager):
    use_in_migrations = True


class ReceiveItem(BaseUuidModel):
    receive_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    receive_item_datetime = models.DateTimeField(default=timezone.now)

    receive = models.ForeignKey(Receive, on_delete=models.PROTECT, null=True, blank=False)

    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT, null=True, blank=False)

    lot = models.ForeignKey(
        Lot,
        verbose_name="Batch",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    reference = models.CharField(max_length=150, default=NULL_STRING, blank=False)

    name = models.CharField(
        max_length=200, default=NULL_STRING, blank=True, help_text="Leave blank to use default"
    )

    container = models.ForeignKey(
        Container,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"may_receive_as": True},
    )

    container_unit_qty = models.DecimalField(
        verbose_name="Container unit quantity",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
        validators=[MinValueValidator(Decimal("1.0"))],
        help_text=(
            "Number of units in the container(s). "
            "Must be the same for all containers in the record."
        ),
    )

    item_qty_received = models.IntegerField(
        verbose_name="Number of containers received",
        null=True,
        blank=False,
        validators=[MinValueValidator(1)],
        help_text="Partial containers should be received separately",
    )

    unit_qty_received = models.DecimalField(
        verbose_name="Unit quantity received",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("1.0"))],
        help_text=(
            "number of containers x container unit qty, e.g. 10 x Bottle of 128 = 1280. "
            "Quantiy will recalculate after save."
        ),
    )

    comment = models.TextField(default=NULL_STRING, blank=True)

    task_id = models.UUIDField(null=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.receive_item_identifier}:"
            f"{self.order_item.product.name}"
            f" | {self.container.display_name}"
        )

    def save(self, *args, **kwargs):
        if not self.receive_item_identifier:
            self.receive_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.receive:
            raise ReceiveItemError("Receive may not be null.")
        if not self.container:
            raise ReceiveItemError("Container may not be null.")
        if not self.order_item:
            raise ReceiveItemError("OrderItem may not be null.")
        if not self.lot:
            raise ReceiveItemError("Lot may not be null.")
        if self.container_unit_qty > Decimal("1.0"):
            self.unit_qty_received = self.item_qty_received * self.container_unit_qty
        else:
            self.unit_qty_received = self.item_qty_received
        if not self.name:
            self.name = f"{self.order_item.product.name} | {self.container.display_name}"
        if not self.container.may_receive_as:
            raise InvalidContainer(
                "Invalid container. Container is not configured for receiving. "
                f"Got {self.container}"
            )
        if self.order_item.product.assignment != self.lot.assignment:
            raise ReceiveError("Lot number assignment does not match product assignment!")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Receive item"
        verbose_name_plural = "Receive items"
