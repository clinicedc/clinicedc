from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...choices import STOCK_STATUS
from ...constants import ALLOCATED, AVAILABLE, ZERO_ITEM
from ...exceptions import AllocationError, AssignmentError
from ...utils import get_random_code
from .allocation import Allocation

# from .confirmation import Confirmation
from .container import Container

# from .dispense import Dispense
from .location import Location
from .lot import Lot
from .managers import StockManager
from .product import Product
from .receive_item import ReceiveItem
from .repack_request import RepackRequest


class Stock(BaseUuidModel):
    stock_identifier = models.CharField(
        verbose_name="Internal stock identifier",
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text="A unique alphanumeric code",
    )

    stock_datetime = models.DateTimeField(
        default=timezone.now, help_text="date stock record created"
    )

    receive_item = models.ForeignKey(
        ReceiveItem, on_delete=models.PROTECT, null=True, blank=False
    )

    repack_request = models.ForeignKey(
        RepackRequest, on_delete=models.PROTECT, null=True, blank=True
    )

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock",
        related_name="source_stock",
        on_delete=models.PROTECT,
        null=True,
    )

    confirmed = models.BooleanField(
        default=False,
        help_text=(
            "True if stock was labelled and confirmed; "
            "False if stock was received/repacked but never confirmed."
        ),
    )
    confirmed_datetime = models.DateTimeField(null=True, blank=True)

    confirmed_by = models.CharField(max_length=150, default="", blank=True)

    allocation = models.OneToOneField(
        Allocation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Subject allocation",
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    lot = models.ForeignKey(
        Lot, verbose_name="Batch", on_delete=models.PROTECT, null=True, blank=False
    )

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    qty = models.DecimalField(
        null=True,
        blank=False,
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
        help_text="Difference of qty_in and qty_out",
    )

    qty_in = models.DecimalField(
        null=True,
        blank=False,
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Container qty, e.g. 1 bucket, 1 bottle, etc",
    )

    qty_out = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Container qty, e.g. 1 bucket, 1 bottle, etc",
    )

    unit_qty_in = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0)],
        help_text="Number of units in this container, e.g. 128 tablets. See post-save signal",
    )

    unit_qty_out = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0)],
        help_text="Number of units from this container, e.g. 128 tablets",
    )

    status = models.CharField(max_length=25, choices=STOCK_STATUS, default=AVAILABLE)

    description = models.CharField(max_length=100, default="", blank=True)

    stored_at_site = models.BooleanField(default=False)

    subject_identifier = models.CharField(max_length=50, default="", blank=True)

    objects = StockManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code}: {self.description}"

    def save(self, *args, **kwargs):
        if not self.stock_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.stock_identifier = f"{next_id:010d}"
            self.code = get_random_code(self.__class__, 6, 10000)
            self.product = self.get_receive_item().order_item.product
        if not self.description:
            self.description = f"{self.product.name} - {self.container.name}"
        self.verify_assignment_or_raise()
        self.verify_assignment_or_raise(self.from_stock)
        self.update_status()
        # do this in the post-save signal?
        # self.unit_qty_in = Decimal(self.qty_in) * Decimal(self.container.qty)
        super().save(*args, **kwargs)

    def update_transferred(self) -> bool:
        return (
            self.allocation
            and self.allocation.stock_request_item.stock_request.location == self.location
            and self.container.may_request_as
        )

    def verify_assignment_or_raise(
        self, stock: models.ForeignKey[Stock] | None = None
    ) -> None:
        """Verify that the LOT and PRODUCT assignments match."""
        if not stock:
            stock = self
        if stock.product.assignment != stock.lot.assignment:
            raise AssignmentError("Lot number assignment does not match product assignment!")
        if self.allocation and self.allocation.assignment != stock.lot.assignment:
            raise AllocationError(
                f"Allocation assignment does not match lot assignment! Got {self.code}."
            )

    def update_status(self):
        if self.allocation:
            self.status = ALLOCATED
        elif self.qty_out == self.qty_in:
            self.status = ZERO_ITEM
        else:
            self.status = AVAILABLE

    def get_receive_item(self) -> ReceiveItem:
        """Recursively fetch the original receive item."""
        obj: Stock = self
        receive_item = self.receive_item
        while not receive_item:
            obj = obj.from_stock
            receive_item = obj.receive_item
        return receive_item

    @property
    def unit_qty(self):
        """Unit qty on hand"""
        return self.unit_qty_in - self.unit_qty_out

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
