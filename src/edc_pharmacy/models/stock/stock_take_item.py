from __future__ import annotations

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

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code}: {self.get_status_display()}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock take item"
        verbose_name_plural = "Stock take items"
        ordering = ["status", "code"]
