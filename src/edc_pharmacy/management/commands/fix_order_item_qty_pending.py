"""Validate and optionally correct unit_qty_pending and unit_qty_received
on every OrderItem.

The signal that keeps these columns in sync (receive_item_on_post_save)
uses update_fields, so it is bypassed by any direct queryset update.
Old records created before the signal existed may also have stale or
NULL values.  This command recalculates both columns from first
principles using the ReceiveItem ledger.

Calculation
-----------
    unit_qty_received = SUM(receive_item.unit_qty_received)
                        for all ReceiveItems linked to the OrderItem
    unit_qty_pending  = unit_qty_ordered - unit_qty_received

Exit codes
----------
0 — all checked, no discrepancies (or --fix applied successfully)
1 — discrepancies found (and --fix not requested)
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum

from ...models import OrderItem, ReceiveItem


class Command(BaseCommand):
    help = (
        "Validate unit_qty_pending / unit_qty_received on every OrderItem "
        "and optionally correct stale or NULL values."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            default=False,
            help="Write corrected values back to the database (default: report only).",
        )
        parser.add_argument(
            "--order",
            metavar="ORDER_IDENTIFIER",
            default=None,
            help="Limit to a single order (by order_identifier).",
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        order_filter = options["order"]

        qs = OrderItem.objects.select_related("order", "product").order_by(
            "order__order_datetime", "order_item_identifier"
        )
        if order_filter:
            qs = qs.filter(order__order_identifier=order_filter)

        # Pre-aggregate all ReceiveItem totals in a single query
        totals = {
            row["order_item_id"]: row["total"]
            for row in ReceiveItem.objects.values("order_item_id").annotate(
                total=Sum("unit_qty_received")
            )
        }

        discrepancies = []
        checked = 0

        for oi in qs:
            checked += 1
            expected_received = totals.get(oi.pk) or Decimal("0.0")
            expected_pending = (oi.unit_qty_ordered or Decimal("0.0")) - expected_received

            received_ok = oi.unit_qty_received == expected_received
            pending_ok = oi.unit_qty_pending == expected_pending

            if not received_ok or not pending_ok:
                discrepancies.append(
                    {
                        "order_item": oi,
                        "current_received": oi.unit_qty_received,
                        "expected_received": expected_received,
                        "current_pending": oi.unit_qty_pending,
                        "expected_pending": expected_pending,
                    }
                )

        self.stdout.write(f"Checked {checked} order item(s).")

        if not discrepancies:
            self.stdout.write(self.style.SUCCESS("All order items are consistent. Nothing to do."))
            return

        self.stdout.write(
            self.style.WARNING(f"Found {len(discrepancies)} discrepancy(ies):\n")
        )

        header = (
            f"  {'Order':<15} {'Item':<15} "
            f"{'recv (cur)':<14} {'recv (exp)':<14} "
            f"{'pend (cur)':<14} {'pend (exp)':<14}"
        )
        self.stdout.write(header)
        self.stdout.write("  " + "-" * (len(header) - 2))

        for d in discrepancies:
            oi = d["order_item"]
            self.stdout.write(
                f"  {oi.order.order_identifier:<15} {oi.order_item_identifier:<15} "
                f"{str(d['current_received']):<14} {str(d['expected_received']):<14} "
                f"{str(d['current_pending']):<14} {str(d['expected_pending']):<14}"
            )

        if fix:
            fixed = 0
            for d in discrepancies:
                oi = d["order_item"]
                oi.unit_qty_received = d["expected_received"]
                oi.unit_qty_pending = d["expected_pending"]
                oi.save(update_fields=["unit_qty_received", "unit_qty_pending"])
                fixed += 1
            self.stdout.write(self.style.SUCCESS(f"\nCorrected {fixed} order item(s)."))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    "\nRun with --fix to write corrections to the database."
                )
            )
            raise SystemExit(1)
