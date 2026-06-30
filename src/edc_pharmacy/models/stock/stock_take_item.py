from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import PROTECT

from edc_model.models import BaseUuidModel, HistoricalRecords

from .stock_take import StockTake

MATCHED = "matched"
MISSING = "missing"
UNEXPECTED = "unexpected"

STOCK_TAKE_ITEM_STATUS = (
    (MATCHED, "Matched"),
    (MISSING, "Missing"),
    (UNEXPECTED, "Unexpected"),
)


class StockTakeItem(BaseUuidModel):
    """One row per stock item outcome in a stock take.

    matched    — code was expected (in bin) and scanned
    missing    — code was expected (in bin) but NOT scanned
    unexpected — code was scanned but NOT registered in the bin
    """

    stock_take = models.ForeignKey(
        StockTake,
        on_delete=PROTECT,
        related_name="items",
    )

    stock = models.ForeignKey(
        "edc_pharmacy.Stock",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="Null if scanned code not found in the system.",
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
    )

    status = models.CharField(
        max_length=15,
        choices=STOCK_TAKE_ITEM_STATUS,
    )

    stock_transaction = models.ForeignKey(
        "edc_pharmacy.StockTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=(
            "The ledger transaction that resolved this discrepancy, if any. "
            "Set when a correction (e.g. lost/damaged/expired or move-to-bin) is "
            "applied from the stock take. SET_NULL so the append-only ledger can be "
            "rebuilt without being blocked."
        ),
    )

    # Acknowledgement — for an unexpected item that cannot be corrected in the
    # system (not in the system, or in a terminal state such as dispensed). The
    # reviewer records a note instead of a transaction so the row can be cleared.
    acknowledged_datetime = models.DateTimeField(null=True, blank=True)

    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    acknowledged_note = models.TextField(default="", blank=True)

    history = HistoricalRecords()

    @property
    def resolved(self) -> bool:
        """True if a correction has been linked to this discrepancy."""
        return self.stock_transaction_id is not None

    @property
    def acknowledged(self) -> bool:
        """True if reviewed and cleared without an in-system correction."""
        return self.acknowledged_datetime is not None

    @property
    def handled(self) -> bool:
        """True if the discrepancy is resolved or acknowledged."""
        return self.resolved or self.acknowledged

    @property
    def cannot_add_reason(self) -> str:
        """Why an unexpected item cannot be added to a bin, else empty string.

        Either the code is not in the system, or the stock is in a terminal
        state (e.g. dispensed). Such items are cleared with *acknowledge*.
        """
        if self.status != UNEXPECTED:
            return ""
        if self.stock is None:
            return "not in the system"
        if self.stock.is_terminal:
            return f"already {self.stock.terminal_reason}"
        return ""

    def __str__(self):
        return f"{self.code}: {self.get_status_display()}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock take item"
        verbose_name_plural = "Stock take items"
        ordering = ("status", "code")
