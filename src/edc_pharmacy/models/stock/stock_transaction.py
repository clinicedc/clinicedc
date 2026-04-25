from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...choices import STOCK_TRANSACTION_CHOICES


class StockTransaction(BaseUuidModel):
    """Append-only ledger row. One row per transition on one Stock item.

    The ``state_after`` JSONField is a snapshot of Stock's cached columns
    immediately after this transaction, making "why is this in this state?"
    a single-query answer and enabling V2 log-replay reconciliation.
    """

    stock = models.ForeignKey(
        "edc_pharmacy.Stock",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    transaction_datetime = models.DateTimeField(default=timezone.now, db_index=True)

    transaction_type = models.CharField(
        max_length=50,
        choices=STOCK_TRANSACTION_CHOICES,
        db_index=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
    )

    reason = models.CharField(max_length=200, default="", blank=True)

    # Signed quantity deltas (0 if not applicable to this transaction type).
    qty_delta = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal("0"))
    unit_qty_delta = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal("0"))

    # Location movement.
    from_location = models.ForeignKey(
        "edc_pharmacy.Location", on_delete=models.PROTECT, null=True, related_name="+"
    )
    to_location = models.ForeignKey(
        "edc_pharmacy.Location", on_delete=models.PROTECT, null=True, related_name="+"
    )

    # Allocation movement.
    from_allocation = models.ForeignKey(
        "edc_pharmacy.Allocation", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    to_allocation = models.ForeignKey(
        "edc_pharmacy.Allocation", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    # Storage bin movement.
    from_bin = models.ForeignKey(
        "edc_pharmacy.StorageBin", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    to_bin = models.ForeignKey(
        "edc_pharmacy.StorageBin", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    # Source business-object FKs (at most one populated per transaction).
    receive_item = models.ForeignKey(
        "edc_pharmacy.ReceiveItem", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    repack_request = models.ForeignKey(
        "edc_pharmacy.RepackRequest", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    stock_transfer_item = models.ForeignKey(
        "edc_pharmacy.StockTransferItem",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    dispense_item = models.ForeignKey(
        "edc_pharmacy.DispenseItem", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    stock_adjustment = models.ForeignKey(
        "edc_pharmacy.StockAdjustment",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    # return_item FK added when ReturnItem model is introduced.

    # Reversal support — V1 schema, V2 machinery.
    # At most one active reversal per original row (enforced in application layer for MySQL).
    reverses = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversed_by",
    )

    # Post-delta snapshot of Stock's cached columns for audit and replay.
    state_after = models.JSONField(default=dict)

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transaction"
        verbose_name_plural = "Stock transactions"
        indexes = [
            models.Index(fields=["stock", "-transaction_datetime"]),
            models.Index(fields=["transaction_type", "-transaction_datetime"]),
        ]
