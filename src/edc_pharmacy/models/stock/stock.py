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
from ...exceptions import AllocationError, AssignmentError, StockError
from ...transaction_log import is_apply_delta_active
from ...utils import get_random_code
from .allocation import Allocation
from .container import Container
from .location import Location
from .lot import Lot
from .managers import StockManager
from .product import Product
from .receive_item import ReceiveItem
from .repack_request import RepackRequest

# Fields that may only be mutated via apply_transaction / _apply_delta.
# Any save() that changes one of these without the sentinel active raises StockError.
GUARDED_FIELDS = frozenset(
    {
        "confirmed",
        "confirmed_at_location",
        "in_transit",
        "stored_at_location",
        "dispensed",
        "destroyed",
        "return_requested",
        "quarantined",
        "damaged",
        "lost",
        "expired",
        "voided",
        "subject_identifier",
        "allocation_id",
    }
)


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

    allocation = models.ForeignKey(
        Allocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=(
            "Sticky pointer to the most recent Allocation for this stock item. "
            "Preserved across dispense, damage, destroy, expire, etc. for audit; "
            "cleared only when the stock is repooled (returned and made available again). "
            "To check whether the allocation is currently active, also test "
            "`allocation.ended_datetime IS NULL`."
        ),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    lot = models.ForeignKey(
        Lot, verbose_name="Batch", on_delete=models.PROTECT, null=True, blank=False
    )

    container = models.ForeignKey(Container, on_delete=models.PROTECT, null=True, blank=False)

    container_unit_qty = models.DecimalField(
        verbose_name="Units per container",
        null=True,
        blank=False,
        decimal_places=2,
        max_digits=20,
        help_text="Number of units per container. ",
    )

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

    in_transit = models.BooleanField(default=False)

    confirmed_at_location = models.BooleanField(default=False)

    stored_at_location = models.BooleanField(default=False)

    dispensed = models.BooleanField(default=False)

    destroyed = models.BooleanField(default=False)

    # New flags added for returns workflow.
    return_requested = models.BooleanField(default=False)
    quarantined = models.BooleanField(default=False)
    damaged = models.BooleanField(default=False)
    lost = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    voided = models.BooleanField(default=False)

    subject_identifier = models.CharField(
        max_length=50, default="", blank=True, editable=False
    )

    # Temporary flag: marks stocks whose cached columns are in an irreconcilable
    # state due to pre-refactor data corruption. Excluded from bootstrap and
    # ledger checks. Drop after the transition is stable.
    invalid_state = models.BooleanField(
        default=False,
        help_text="Pre-refactor data corruption; excluded from ledger bootstrap/checks.",
    )

    objects = StockManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code}: {self.product.name} - {self.container.container_type}"

    def save(self, *args, **kwargs):
        if not self.stock_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.stock_identifier = f"{next_id:010d}"
            self.code = get_random_code(self.__class__, 6, 10000)
            self.product = self.get_receive_item().order_item.product
        self.verify_assignment_or_raise()
        self.verify_assignment_or_raise(self.from_stock)
        self.update_status()
        self._check_guarded_fields_or_raise()
        super().save(*args, **kwargs)

    def _check_guarded_fields_or_raise(self) -> None:
        """Raise if a guarded field changed without apply_transaction being active."""
        if is_apply_delta_active() or not self.pk:
            return
        try:
            original = Stock.objects.get(pk=self.pk)
        except Stock.DoesNotExist:
            return
        changed = [f for f in GUARDED_FIELDS if getattr(self, f) != getattr(original, f)]
        if changed:
            raise StockError(
                f"Mutating {changed} on Stock requires apply_transaction. "
                "Do not write guarded fields directly."
            )

    def update_transferred(self) -> bool:
        # Sticky-pointer policy: only an *active* allocation indicates a live
        # transfer-to-subject relationship. A dispensed/damaged/etc. bottle
        # still has Stock.allocation set but is no longer in transfer flow.
        return bool(
            self.allocation
            and self.allocation.ended_datetime is None
            and self.allocation.stock_request_item.stock_request.location
            == self.location
            and self.container.may_request_as
        )

    def verify_assignment_or_raise(self, stock: models.ForeignKey[Stock] = None) -> None:
        """Verify that the LOT and PRODUCT assignments match."""
        if not stock:
            stock = self
        if stock.product.assignment != stock.lot.assignment:
            raise AssignmentError("Lot number assignment does not match product assignment!")
        if (
            self.allocation
            and self.allocation.assignment != stock.lot.assignment
        ):
            raise AllocationError(
                f"Allocation assignment does not match lot assignment! Got {self.code}."
            )

    def update_status(self):
        # Note: Stock.allocation is a sticky pointer (preserved past dispense,
        # damage, etc.). For "is currently allocated", also require that the
        # Allocation row has not been ended.
        is_active_allocation = bool(
            self.allocation_id
            and self.allocation
            and self.allocation.ended_datetime is None
        )
        if is_active_allocation:
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
