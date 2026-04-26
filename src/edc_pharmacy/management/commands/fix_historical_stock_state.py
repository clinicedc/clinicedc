"""One-time data fix for Stock rows whose cached columns are inconsistent
with the StockTransaction ledger due to gaps in the pre-refactor signal
handlers.

Three classes of inconsistency are corrected:

1. **in_transit stuck True** — the old `stock_transfer_item_on_post_save`
   signal set ``in_transit=True`` when a transfer item was created but no
   corresponding signal ever cleared it when the stock was confirmed at the
   destination.  Fix: set ``in_transit=False`` for every Stock that has a
   ``ConfirmationAtLocationItem`` (i.e. it was received at the site) or is
   already ``dispensed`` (which also implies confirmed + stored).

2. **allocation not nulled after dispense** — ``dispense_item_on_post_save``
   set ``dispensed=True`` but never cleared the ``allocation`` FK.  Fix: null
   ``allocation_id`` for every Stock where ``dispensed=True``.

3. **bootstrapped TXN_RECEIVED qty_delta=0** — the bootstrap command created
   TXN_RECEIVED rows with zero qty deltas.  Because each Stock container
   represents exactly 1 unit of qty_in, the correct delta is +1 (and
   +container_unit_qty for unit_qty_in).  Fix: update those ledger rows in
   bulk.

This command is idempotent.  Re-running it is safe.

Exit codes
----------
0 — completed successfully
1 — at least one error occurred
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from ...constants import TXN_REPACK_CONSUMED, TXN_RECEIVED, ZERO_ITEM
from ...models import Stock, StockTransaction


class Command(BaseCommand):
    help = (
        "One-time data fix: correct Stock.in_transit, Stock.allocation, and "
        "bootstrapped TXN_RECEIVED qty deltas to match the StockTransaction ledger."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Report what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        errors = 0

        errors += self._fix_in_transit(dry_run)
        errors += self._fix_allocation_after_dispense(dry_run)
        errors += self._fix_bootstrapped_qty_deltas(dry_run)
        errors += self._fix_repack_consumed(dry_run)
        errors += self._mark_invalid_stocks(dry_run)

        if errors:
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # Fix 1: in_transit stuck True
    # ------------------------------------------------------------------

    def _fix_in_transit(self, dry_run: bool) -> int:
        # Two disjoint cases — keep as separate queries to avoid MySQL's
        # "can't specify target table in FROM clause" restriction on
        # self-referencing subquery UPDATEs.
        #
        # Case A: confirmed at location (JOIN to CALI — different table, fine).
        qs_cali = Stock.objects.filter(
            in_transit=True, confirmationatlocationitem__isnull=False
        )
        # Case B: dispensed (implies confirmed+stored — simple column filter).
        qs_dispensed = Stock.objects.filter(in_transit=True, dispensed=True)

        count = qs_cali.count() + qs_dispensed.count()
        self.stdout.write(
            f"[in_transit] {count} stocks to fix "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs_cali.update(in_transit=False)
                    updated += qs_dispensed.update(in_transit=False)
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 2: allocation FK not nulled after dispense
    # ------------------------------------------------------------------

    def _fix_allocation_after_dispense(self, dry_run: bool) -> int:
        qs = Stock.objects.filter(dispensed=True, allocation__isnull=False)
        count = qs.count()
        self.stdout.write(
            f"[allocation] {count} dispensed stocks with non-null allocation "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    # Dispensed stocks have qty_out==qty_in so status=ZERO_ITEM.
                    updated = qs.update(allocation=None, status=ZERO_ITEM)
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 3: bootstrapped TXN_RECEIVED qty deltas
    # ------------------------------------------------------------------

    def _fix_bootstrapped_qty_deltas(self, dry_run: bool) -> int:
        qs = StockTransaction.objects.filter(
            transaction_type=TXN_RECEIVED,
            state_after={"bootstrapped": True},
            qty_delta=Decimal("0"),
        ).select_related("stock")

        count = qs.count()
        self.stdout.write(
            f"[qty_delta] {count} bootstrapped TXN_RECEIVED rows to fix "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if not count or dry_run:
            return 0

        errors = 0
        updated = 0
        # Process in chunks to avoid locking the whole table.
        for txn in qs.iterator(chunk_size=500):
            unit_qty = txn.stock.container_unit_qty or Decimal("0")
            try:
                StockTransaction.objects.filter(pk=txn.pk).update(
                    qty_delta=Decimal("1"),
                    unit_qty_delta=unit_qty,
                )
                updated += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"  ERROR on txn {txn.pk}: {exc}")
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(f"  Updated {updated} rows.")
            if not errors
            else self.style.WARNING(f"  Updated {updated} rows, {errors} errors.")
        )
        return 1 if errors else 0

    # ------------------------------------------------------------------
    # Fix 4: missing TXN_REPACK_CONSUMED for repacked bulk stocks
    # ------------------------------------------------------------------

    def _fix_repack_consumed(self, dry_run: bool) -> int:
        from ...models.stock.repack_request import RepackRequest

        # Find repack requests that have no corresponding TXN_REPACK_CONSUMED row.
        already_logged = set(
            StockTransaction.objects.filter(
                transaction_type=TXN_REPACK_CONSUMED,
            )
            .exclude(repack_request=None)
            .values_list("repack_request_id", flat=True)
        )
        pending = RepackRequest.objects.exclude(pk__in=already_logged).select_related(
            "from_stock"
        )

        count = pending.count()
        self.stdout.write(
            f"[repack_consumed] {count} RepackRequest rows missing TXN_REPACK_CONSUMED "
            f"({'dry-run' if dry_run else 'will create'})"
        )
        if not count or dry_run:
            return 0

        errors = 0
        created = 0
        for rr in pending.iterator(chunk_size=200):
            unit_qty = rr.unit_qty_processed or Decimal("0")
            if unit_qty == 0:
                continue
            try:
                StockTransaction.objects.bulk_create([
                    StockTransaction(
                        stock=rr.from_stock,
                        transaction_type=TXN_REPACK_CONSUMED,
                        actor=None,
                        reason="bootstrapped",
                        transaction_datetime=rr.repack_datetime,
                        created=rr.repack_datetime,
                        modified=rr.repack_datetime,
                        qty_delta=Decimal("0"),
                        unit_qty_delta=-unit_qty,
                        from_location_id=rr.from_stock.location_id,
                        to_location_id=rr.from_stock.location_id,
                        repack_request=rr,
                        state_after={"bootstrapped": True},
                    )
                ])
                created += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"  ERROR on repack_request {rr.pk}: {exc}")
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(f"  Created {created} rows.")
            if not errors
            else self.style.WARNING(f"  Created {created} rows, {errors} errors.")
        )
        return 1 if errors else 0

    # ------------------------------------------------------------------
    # Fix 5: mark irreconcilable stocks as invalid_state=True
    # ------------------------------------------------------------------

    def _mark_invalid_stocks(self, dry_run: bool) -> int:
        # Stocks that are dispensed but have no DispenseItem AND no allocation —
        # the dispensed flag was set without going through the proper workflow.
        # These cannot be reconciled by the ledger.
        qs = Stock.objects.filter(
            dispensed=True,
            invalid_state=False,
            allocation__isnull=True,
            dispenseitem__isnull=True,
        )

        count = qs.count()
        self.stdout.write(
            f"[invalid_state] {count} bulk stocks incorrectly marked dispensed "
            f"({'dry-run' if dry_run else 'will flag'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(invalid_state=True)
                self.stdout.write(self.style.SUCCESS(f"  Flagged {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0
