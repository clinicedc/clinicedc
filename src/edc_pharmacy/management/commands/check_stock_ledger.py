"""Verify that Stock cache columns are consistent with the StockTransaction
ledger.

For each stock, replays the ordered transaction sequence to derive the
expected value of every guarded boolean flag, allocation state, and
location.  Any mismatch between expected and actual is reported as a
discrepancy.

Quantity columns (qty_in / qty_out / unit_qty_in / unit_qty_out) are
checked separately using ledger deltas.

Stocks with no transactions are reported as a distinct group; they
indicate either genuinely inert stock (never confirmed) or a gap in the
ledger that may need investigation.

Exit codes
----------
0 — all checked, no discrepancies
1 — at least one discrepancy found
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from ...constants import (
    TXN_ALLOCATED,
    TXN_ALLOCATION_ENDED,
    TXN_BIN_MOVED,
    TXN_DAMAGED,
    TXN_DISPENSED,
    TXN_EXPIRED,
    TXN_LOST,
    TXN_RECEIVED,
    TXN_REPACK_CONSUMED,
    TXN_REPACK_PRODUCED,
    TXN_RETURN_DISPATCHED,
    TXN_RETURN_DISPOSITION_DESTROYED,
    TXN_RETURN_DISPOSITION_QUARANTINED,
    TXN_RETURN_DISPOSITION_REPOOLED,
    TXN_RETURN_RECEIVED,
    TXN_RETURN_REQUESTED,
    TXN_STORED,
    TXN_TRANSFER_DISPATCHED,
    TXN_TRANSFER_RECEIVED,
    TXN_VOIDED,
)
from ...models import Stock, StockTransaction


def _replay(txns) -> dict:
    """Derive expected Stock state by replaying an ordered transaction list.

    Returns a dict whose keys match Stock field names (plus ``has_allocation``
    as a proxy for ``allocation_id is not None``).  Only fields whose value
    is touched by at least one transaction type are included.
    """
    state: dict = {
        "confirmed": False,
        "in_transit": False,
        "confirmed_at_location": False,
        "stored_at_location": False,
        "dispensed": False,
        "destroyed": False,
        "damaged": False,
        "lost": False,
        "expired": False,
        "voided": False,
        "return_requested": False,
        "quarantined": False,
        "has_allocation": False,
        "location_id": None,
        "qty_in": Decimal(0),
        "qty_out": Decimal(0),
        "unit_qty_in": Decimal(0),
        "unit_qty_out": Decimal(0),
    }

    for txn in txns:
        tt = txn.transaction_type
        if txn.to_location_id:
            state["location_id"] = txn.to_location_id

        if tt == TXN_RECEIVED:
            state["confirmed"] = True

        elif tt in (TXN_REPACK_CONSUMED, TXN_REPACK_PRODUCED, TXN_BIN_MOVED):
            pass

        elif tt == TXN_ALLOCATED:
            state["has_allocation"] = True

        elif tt == TXN_ALLOCATION_ENDED:
            state["has_allocation"] = False

        elif tt == TXN_TRANSFER_DISPATCHED:
            state["in_transit"] = True
            state["stored_at_location"] = False
            state["confirmed_at_location"] = False

        elif tt == TXN_TRANSFER_RECEIVED:
            state["in_transit"] = False
            state["confirmed_at_location"] = True

        elif tt == TXN_STORED:
            state["stored_at_location"] = True

        elif tt == TXN_DISPENSED:
            state["dispensed"] = True
            state["stored_at_location"] = False
            state["in_transit"] = False
            state["has_allocation"] = False

        elif tt == TXN_RETURN_REQUESTED:
            state["return_requested"] = True

        elif tt == TXN_RETURN_DISPATCHED:
            # Allocation is intentionally NOT ended at dispatch — it is held
            # until final disposition at central (repooled/quarantined/destroyed).
            state["in_transit"] = True
            state["stored_at_location"] = False
            state["confirmed_at_location"] = False
            state["return_requested"] = False

        elif tt == TXN_RETURN_RECEIVED:
            state["in_transit"] = False
            state["confirmed_at_location"] = False

        elif tt == TXN_RETURN_DISPOSITION_REPOOLED:
            state["quarantined"] = False
            state["has_allocation"] = False

        elif tt == TXN_RETURN_DISPOSITION_QUARANTINED:
            state["quarantined"] = True
            state["has_allocation"] = False

        elif tt == TXN_RETURN_DISPOSITION_DESTROYED:
            state["destroyed"] = True
            state["quarantined"] = False
            state["has_allocation"] = False

        elif tt == TXN_DAMAGED:
            state["damaged"] = True
            state["stored_at_location"] = False
            state["has_allocation"] = False

        elif tt == TXN_LOST:
            state["lost"] = True
            state["stored_at_location"] = False
            state["has_allocation"] = False

        elif tt == TXN_EXPIRED:
            state["expired"] = True
            state["stored_at_location"] = False
            state["has_allocation"] = False

        elif tt == TXN_VOIDED:
            state["voided"] = True
            state["stored_at_location"] = False
            state["has_allocation"] = False

        # Accumulate signed qty deltas.
        if txn.qty_delta > 0:
            state["qty_in"] += txn.qty_delta
        elif txn.qty_delta < 0:
            state["qty_out"] += abs(txn.qty_delta)
        if txn.unit_qty_delta > 0:
            state["unit_qty_in"] += txn.unit_qty_delta
        elif txn.unit_qty_delta < 0:
            state["unit_qty_out"] += abs(txn.unit_qty_delta)

    return state


def _compare(stock: Stock, expected: dict) -> dict[str, dict]:
    """Return {field: {expected, actual}} for every mismatch."""
    mismatches: dict[str, dict] = {}

    bool_fields = (
        "confirmed",
        "in_transit",
        "confirmed_at_location",
        "stored_at_location",
        "dispensed",
        "destroyed",
        "damaged",
        "lost",
        "expired",
        "voided",
        "return_requested",
        "quarantined",
    )
    for field in bool_fields:
        actual = getattr(stock, field)
        exp = expected[field]
        if actual != exp:
            mismatches[field] = {"expected": exp, "actual": actual}

    # Allocation.
    actual_alloc = stock.current_allocation_id is not None
    if actual_alloc != expected["has_allocation"]:
        mismatches["has_allocation"] = {
            "expected": expected["has_allocation"],
            "actual": actual_alloc,
        }

    # Location (only checked if the log recorded a location change).
    if expected["location_id"] is not None and stock.location_id != expected["location_id"]:
        mismatches["location_id"] = {
            "expected": expected["location_id"],
            "actual": stock.location_id,
        }

    # Quantities (skip for bootstrapped-only ledgers where all deltas are 0).
    total_delta = sum(
        abs(v)
        for k, v in expected.items()
        if k in ("qty_in", "qty_out", "unit_qty_in", "unit_qty_out")
    )
    if total_delta > 0:
        for field in ("qty_in", "qty_out", "unit_qty_in", "unit_qty_out"):
            actual_qty = getattr(stock, field) or Decimal(0)
            if actual_qty != expected[field]:
                mismatches[field] = {
                    "expected": expected[field],
                    "actual": actual_qty,
                }

    return mismatches


class Command(BaseCommand):
    help = (
        "Verify Stock cache columns are consistent with the StockTransaction "
        "ledger. Exits with code 1 if any discrepancy is found."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--stock-code",
            type=str,
            default=None,
            help="Check a single stock code.",
        )
        parser.add_argument(
            "--show-ok",
            action="store_true",
            default=False,
            help="Also print stocks that passed (verbose).",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        stock_code: str | None = options["stock_code"]
        show_ok: bool = options["show_ok"]

        qs = Stock.objects.prefetch_related(
            Prefetch(
                "transactions",
                queryset=StockTransaction.objects.order_by("transaction_datetime"),
            )
        ).select_related("current_allocation")

        if stock_code:
            qs = qs.filter(code=stock_code)

        total = ok = discrepancy_count = no_txn = invalid_skipped = 0
        discrepancies: list[tuple[str, dict]] = []

        for stock in qs.iterator(chunk_size=500):
            total += 1

            if stock.invalid_state:
                invalid_skipped += 1
                continue

            txns = list(stock.transactions.all())

            if not txns:
                no_txn += 1
                continue

            expected = _replay(txns)
            mismatches = _compare(stock, expected)

            if mismatches:
                discrepancy_count += 1
                discrepancies.append((stock.code, mismatches))
            else:
                ok += 1
                if show_ok:
                    self.stdout.write(f"  OK  {stock.code}")

        # Summary.
        self.stdout.write("")
        if discrepancies:
            self.stdout.write(self.style.ERROR(f"DISCREPANCIES ({discrepancy_count}):"))
            for code, fields in discrepancies:
                self.stdout.write(self.style.ERROR(f"  {code}"))
                for field, vals in fields.items():
                    self.stdout.write(
                        f"    {field}: expected={vals['expected']}  actual={vals['actual']}"
                    )
        else:
            self.stdout.write(self.style.SUCCESS("No discrepancies found."))

        invalid_note = (
            f", {invalid_skipped} skipped (invalid_state)" if invalid_skipped else ""
        )
        self.stdout.write(
            f"\nChecked {total} stocks: "
            f"{ok} OK, {discrepancy_count} with discrepancies, "
            f"{no_txn} with no transactions{invalid_note}."
        )

        if discrepancies:
            raise SystemExit(1)
