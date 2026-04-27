"""One-time data fix for Stock rows whose cached columns are inconsistent
with the StockTransaction ledger due to gaps in the pre-refactor signal
handlers.

Five classes of inconsistency are corrected:

1. **in_transit stuck True** — the old ``stock_transfer_item_on_post_save``
   signal set ``in_transit=True`` when a transfer item was created but no
   corresponding signal ever cleared it when the stock was confirmed at the
   destination.  Fix: set ``in_transit=False`` for every Stock that has a
   ``ConfirmationAtLocationItem`` (i.e. it was received at the site) or is
   already ``dispensed`` (which also implies confirmed + stored).

2. **allocation not nulled after dispense** — ``dispense_item_on_post_save``
   set ``dispensed=True`` but never cleared the ``allocation`` FK.  Fix: null
   ``allocation_id`` for every Stock where ``dispensed=True``.

3. **stored_at_location stuck True after dispense** — the old dispense signal
   set ``dispensed=True`` but did not always clear ``stored_at_location``.
   Fix: clear ``stored_at_location`` for every Stock where ``dispensed=True``.

4. **bootstrapped TXN_RECEIVED qty_delta=0** — the bootstrap command created
   TXN_RECEIVED rows with zero qty deltas.  Because each Stock container
   represents exactly 1 unit of qty_in, the correct delta is +1 (and
   +container_unit_qty for unit_qty_in).  Fix: update those ledger rows in
   bulk.

5. **TXN_REPACK_CONSUMED qty_delta=0 when stock.qty_out=1** — the old repack
   workflow incremented ``Stock.qty_out`` to 1 when a container was fully
   consumed, but the bootstrap/fix_repack_consumed path created
   TXN_REPACK_CONSUMED with ``qty_delta=0``.  Fix: set ``qty_delta=-1`` on
   those rows.

6. **Bulk stock at non-central location** — bulk containers (from_stock=None,
   repack_request=None) can only ever be at central.  Fix: set location to
   central for any that have drifted.

7. **Repacked child stock at wrong location** — child bottles created by
   ``process_repack_request`` inherit ``from_stock.location``.  Since repack
   can only happen at central, any child that has not yet been transferred
   (in_transit=False, confirmed_at_location=False, stored_at_location=False,
   dispensed=False) must be at central.  Fix: update location to central for
   those rows.  Items that have already been through a transfer are untouched
   because ``apply_transaction`` already corrected their location.

8. **Bootstrapped TXN_RECEIVED / TXN_ALLOCATED / TXN_REPACK_* with wrong
   from/to location** — bootstrap captured ``stock.location`` which was wrong
   at the time (e.g. the old transfer-dispatch signal had already overwritten
   it to a site before bootstrap ran).  All of these transaction types must
   have central as both from and to location.  Fix: patch from_location and
   to_location to central on all bootstrapped rows of these types.  This is a
   no-op on the first pass (no bootstrap rows yet) and effective on the second
   pass.

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

from ...constants import (
    CENTRAL_LOCATION,
    TXN_ALLOCATED,
    TXN_REPACK_CONSUMED,
    TXN_REPACK_PRODUCED,
    TXN_RECEIVED,
    ZERO_ITEM,
)
from ...models import Stock, StockTransaction
from ...models.stock.location import Location


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
        errors += self._fix_stored_at_location_after_dispense(dry_run)
        errors += self._fix_bootstrapped_qty_deltas(dry_run)
        errors += self._fix_repack_consumed(dry_run)
        errors += self._fix_repack_consumed_qty_delta(dry_run)
        errors += self._mark_invalid_stocks(dry_run)
        errors += self._fix_bulk_stock_location(dry_run)
        errors += self._fix_repack_child_location(dry_run)
        errors += self._fix_bootstrapped_txn_locations(dry_run)

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
        qs = Stock.objects.filter(dispensed=True, current_allocation__isnull=False)
        count = qs.count()
        self.stdout.write(
            f"[allocation] {count} dispensed stocks with non-null current_allocation "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    # Dispensed stocks have qty_out==qty_in so status=ZERO_ITEM.
                    updated = qs.update(current_allocation=None, status=ZERO_ITEM)
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
        # Two sources of existing rows:
        # 1. Rows created by this command (have repack_request FK set).
        # 2. Rows created by bootstrap_stock_transactions (no FK; linked via stock).
        # Both must be excluded to stay idempotent when this command is re-run
        # after bootstrap.
        already_logged_by_fk = set(
            StockTransaction.objects.filter(
                transaction_type=TXN_REPACK_CONSUMED,
            )
            .exclude(repack_request=None)
            .values_list("repack_request_id", flat=True)
        )
        already_logged_by_stock = set(
            StockTransaction.objects.filter(
                transaction_type=TXN_REPACK_CONSUMED,
                repack_request=None,
            )
            .values_list("stock_id", flat=True)
        )
        pending = (
            RepackRequest.objects
            .exclude(pk__in=already_logged_by_fk)
            .exclude(from_stock_id__in=already_logged_by_stock)
            .select_related("from_stock")
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
    # Fix 5: stored_at_location stuck True after dispense
    # ------------------------------------------------------------------

    def _fix_stored_at_location_after_dispense(self, dry_run: bool) -> int:
        """Clear stored_at_location for dispensed stocks.

        The old dispense_item_on_post_save signal set dispensed=True but did
        not always clear stored_at_location.  The ledger replay arrives at
        stored_at_location=False after TXN_DISPENSED; the Stock column should
        match.
        """
        qs = Stock.objects.filter(dispensed=True, stored_at_location=True)
        count = qs.count()
        self.stdout.write(
            f"[stored_at_location] {count} dispensed stocks with stored_at_location=True "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(stored_at_location=False)
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 6: TXN_REPACK_CONSUMED qty_delta=0 when stock.qty_out=1
    # ------------------------------------------------------------------

    def _fix_repack_consumed_qty_delta(self, dry_run: bool) -> int:
        """Set qty_delta=-1 on bootstrapped TXN_REPACK_CONSUMED rows whose
        source stock already has qty_out=1.

        The old repack workflow incremented Stock.qty_out=1 when a container
        was fully consumed.  The bootstrap/fix_repack_consumed path created
        TXN_REPACK_CONSUMED with qty_delta=0, leaving a mismatch between the
        ledger replay (qty_out=0) and the actual column (qty_out=1).
        """
        qs = StockTransaction.objects.filter(
            transaction_type=TXN_REPACK_CONSUMED,
            qty_delta=Decimal("0"),
            stock__qty_out=Decimal("1"),
        )
        count = qs.count()
        self.stdout.write(
            f"[repack_consumed_qty] {count} TXN_REPACK_CONSUMED rows with qty_delta=0 "
            f"but stock.qty_out=1 "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(qty_delta=Decimal("-1"))
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 7: mark irreconcilable stocks as invalid_state=True
    # ------------------------------------------------------------------

    def _mark_invalid_stocks(self, dry_run: bool) -> int:
        # Stocks that are dispensed but have no DispenseItem AND no allocation —
        # the dispensed flag was set without going through the proper workflow.
        # These cannot be reconciled by the ledger.
        qs = Stock.objects.filter(
            dispensed=True,
            invalid_state=False,
            current_allocation__isnull=True,
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

    # ------------------------------------------------------------------
    # Fix 8: bulk stock (from_stock=None) at non-central location
    # ------------------------------------------------------------------

    def _fix_bulk_stock_location(self, dry_run: bool) -> int:
        """Bulk stock can never be at a site — always at central.

        Stock items received directly (from_stock=None, repack_request=None)
        are bulk containers held at central.  If any ended up with a non-central
        location (due to data migration issues or signal bugs), correct them.
        """
        try:
            central_location = Location.objects.get(name=CENTRAL_LOCATION)
        except Location.DoesNotExist:
            self.stderr.write(self.style.ERROR("[bulk_location] Central location not found."))
            return 1

        qs = Stock.objects.filter(
            from_stock__isnull=True,
            repack_request__isnull=True,
        ).exclude(location=central_location)

        count = qs.count()
        self.stdout.write(
            f"[bulk_location] {count} bulk stocks with non-central location "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(location=central_location)
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 9: repacked child stock still at central with wrong location
    # ------------------------------------------------------------------

    def _fix_repack_child_location(self, dry_run: bool) -> int:
        """Repacked children not yet transferred must be at central.

        Child stock items (repack_request not null) are created at central
        and only leave via a stock transfer.  Items that have not yet been
        transferred (in_transit=False, confirmed_at_location=False,
        stored_at_location=False, dispensed=False) must have the central
        location.  Items that have been through a transfer already had their
        location updated by apply_transaction and are left unchanged.
        """
        try:
            central_location = Location.objects.get(name=CENTRAL_LOCATION)
        except Location.DoesNotExist:
            self.stderr.write(
                self.style.ERROR("[repack_child_location] Central location not found.")
            )
            return 1

        qs = Stock.objects.filter(
            repack_request__isnull=False,
            in_transit=False,
            confirmed_at_location=False,
            stored_at_location=False,
            dispensed=False,
        ).exclude(location=central_location)

        count = qs.count()
        self.stdout.write(
            f"[repack_child_location] {count} repacked child stocks with wrong location "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(location=central_location)
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0

    # ------------------------------------------------------------------
    # Fix 10: bootstrapped transactions with wrong from/to location
    # ------------------------------------------------------------------

    def _fix_bootstrapped_txn_locations(self, dry_run: bool) -> int:
        """Correct from_location / to_location on bootstrapped transactions
        that must always be at central.

        - TXN_RECEIVED: all stock arrives at central, so both locations = central.
        - TXN_ALLOCATED: allocation only happens at central.
        - TXN_REPACK_PRODUCED / TXN_REPACK_CONSUMED: repack is a central-only
          operation.

        Bootstrap captured wrong locations for these types when stock.location
        was already wrong (e.g. the old transfer-dispatch signal had already
        overwritten it to a site before bootstrap ran).

        This fix is a no-op on the first pass (no bootstrapped rows yet) and
        effective on the second pass after bootstrap has created the rows.
        """
        try:
            central_location = Location.objects.get(name=CENTRAL_LOCATION)
        except Location.DoesNotExist:
            self.stderr.write(
                self.style.ERROR("[bootstrapped_txn_locations] Central location not found.")
            )
            return 1

        central_only_types = [
            TXN_RECEIVED,
            TXN_ALLOCATED,
            TXN_REPACK_PRODUCED,
            TXN_REPACK_CONSUMED,
        ]
        qs = StockTransaction.objects.filter(
            transaction_type__in=central_only_types,
            state_after={"bootstrapped": True},
        ).exclude(from_location=central_location, to_location=central_location)

        count = qs.count()
        self.stdout.write(
            f"[bootstrapped_txn_locations] {count} bootstrapped transactions "
            f"with wrong from/to location "
            f"({'dry-run' if dry_run else 'will update'})"
        )
        if count and not dry_run:
            try:
                with transaction.atomic():
                    updated = qs.update(
                        from_location=central_location,
                        to_location=central_location,
                    )
                self.stdout.write(self.style.SUCCESS(f"  Updated {updated} rows."))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR: {exc}"))
                return 1
        return 0
