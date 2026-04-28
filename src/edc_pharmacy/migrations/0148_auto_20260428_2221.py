"""Data migration: backfill cached counts and qty fields before
0149 enforces NOT NULL on Order.item_count and the OrderItem qty columns.

Mirrors `fix_order_item_qty_pending --fix`:
  - Order.item_count       <- COUNT(OrderItem) per order
  - OrderItem.unit_qty_ordered  <- item_qty_ordered * container_unit_qty (when NULL)
  - OrderItem.unit_qty_received <- SUM(ReceiveItem.unit_qty_received) per order_item
  - OrderItem.unit_qty_pending  <- unit_qty_ordered - unit_qty_received
  - OrderItem.status / Order.status recomputed from the above

Status string literals are inlined ("new" / "partial" / "complete") rather than
imported, so this migration stays valid even if constants are later moved.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import migrations
from django.db.models import Sum


def backfill(apps, schema_editor):
    Order = apps.get_model("edc_pharmacy", "Order")
    OrderItem = apps.get_model("edc_pharmacy", "OrderItem")
    ReceiveItem = apps.get_model("edc_pharmacy", "ReceiveItem")

    zero = Decimal("0.0")

    # ── Pre-aggregate ReceiveItem totals per order_item in one query ──
    received_totals = {
        row["order_item_id"]: row["total"] or zero
        for row in ReceiveItem.objects.values("order_item_id").annotate(
            total=Sum("unit_qty_received")
        )
    }

    # ── Backfill OrderItem qty fields and status ──
    for oi in OrderItem.objects.all().iterator():
        # unit_qty_ordered: derive from containers * units-per-container if NULL
        if oi.unit_qty_ordered is None:
            if oi.item_qty_ordered is not None and oi.container_unit_qty is not None:
                oi.unit_qty_ordered = (
                    Decimal(oi.item_qty_ordered) * oi.container_unit_qty
                )
            else:
                oi.unit_qty_ordered = zero

        oi.unit_qty_received = received_totals.get(oi.pk, zero)
        oi.unit_qty_pending = oi.unit_qty_ordered - oi.unit_qty_received

        if oi.unit_qty_received == zero:
            oi.status = "new"
        elif oi.unit_qty_received == oi.unit_qty_ordered:
            oi.status = "complete"
        else:
            oi.status = "partial"

        oi.save(
            update_fields=[
                "unit_qty_ordered",
                "unit_qty_received",
                "unit_qty_pending",
                "status",
            ]
        )

    # ── Backfill Order.item_count and Order.status ──
    for order in Order.objects.all().iterator():
        order.item_count = OrderItem.objects.filter(order=order).count()

        agg = OrderItem.objects.filter(order=order).aggregate(
            ordered=Sum("unit_qty_ordered"),
            received=Sum("unit_qty_received"),
        )
        ordered = agg["ordered"] or zero
        received = agg["received"] or zero

        if received == zero:
            order.status = "new"
        elif received == ordered:
            order.status = "complete"
        else:
            order.status = "partial"

        order.save(update_fields=["item_count", "status"])


def noop_reverse(apps, schema_editor):
    # Pure data backfill — irreversible, but safe to no-op so unmigrate works.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("edc_pharmacy", "0147_alter_historicalstocktake_options_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill, noop_reverse),
    ]
