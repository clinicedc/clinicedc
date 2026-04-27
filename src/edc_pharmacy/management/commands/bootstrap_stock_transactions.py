"""Back-fill StockTransaction rows for stock that existed before the
transaction-log refactor.

Each stock that has no existing StockTransaction rows is processed in
lifecycle order:

  RECEIVED → ALLOCATED → TRANSFER_DISPATCHED → TRANSFER_RECEIVED
  → STORED → DISPENSED

The command is idempotent: stocks that already have at least one
StockTransaction row are skipped entirely.

actor is resolved from stock.user_modified or stock.user_created (falling
back through both fields). Unknown usernames resolve to None.

state_after is set to {"bootstrapped": True} for all rows — we cannot
reconstruct the exact intermediate state without replaying the full
event log.

Note before running:
    uv --nodev --no-sources manage.py migrate
    uv --nodev --no-sources manage.py fix_historical_stock_state
    uv --nodev --no-sources manage.py shell -c "from edc_pharmacy.models import StockTransaction; StockTransaction.objects.all().delete()"
    uv --nodev --no-sources manage.py bootstrap_stock_transactions
`   uv --nodev --no-sources manage.py check_stock_ledger
"""

from __future__ import annotations

from decimal import Decimal

from tqdm import tqdm

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from ...constants import (TXN_ALLOCATED, TXN_DISPENSED, TXN_RECEIVED, TXN_REPACK_CONSUMED,
                          TXN_STORED, TXN_TRANSFER_DISPATCHED, TXN_TRANSFER_RECEIVED)
from ...models import Stock, StockTransaction
from ...models.stock import (
    Allocation,
    ConfirmationAtLocationItem,
    DispenseItem,
    StorageBinItem,
)

_BOOTSTRAPPED = {"bootstrapped": True}


def _resolve_actor(username: str | None, cache: dict) -> object:
    """Return a User instance for username, or None. Results are cached."""
    if not username:
        return None
    if username not in cache:
        User = get_user_model()
        try:
            cache[username] = User.objects.get(username=username)
        except User.DoesNotExist:
            cache[username] = None
    return cache[username]


def _txn(
        stock: Stock,
        txn_type: str,
        dt,
        *,
        actor=None,
        from_location_id=None,
        to_location_id=None,
        qty_delta: Decimal = Decimal("0"),
        unit_qty_delta: Decimal = Decimal("0"),
        **fk_kwargs,
) -> StockTransaction:
    username = actor.username if actor else ""
    return StockTransaction(
        stock=stock,
        transaction_type=txn_type,
        actor=actor,
        reason="bootstrapped",
        transaction_datetime=dt,
        created=dt,
        modified=dt,
        qty_delta=qty_delta,
        unit_qty_delta=unit_qty_delta,
        from_location_id=from_location_id or stock.location_id,
        to_location_id=to_location_id or stock.location_id,
        state_after=_BOOTSTRAPPED,
        user_created=username,
        user_modified=username,
        **fk_kwargs,
    )


def _bootstrap_one(stock: Stock, actor_cache: dict) -> list[StockTransaction]:
    """Return unsaved StockTransaction instances for a single stock."""
    rows: list[StockTransaction] = []
    actor = _resolve_actor(stock.user_modified or stock.user_created, actor_cache)

    # Resolve allocation — stock.current_allocation is None for dispensed/ended stocks,
    # but Allocation.code == stock.code so the record is still recoverable.
    allocation = stock.current_allocation or Allocation.objects.filter(
        code=stock.code
    ).first()

    # RECEIVED — qty_in=+1, unit_qty_in=+container_unit_qty.
    if stock.confirmed:
        dt = stock.confirmed_datetime or stock.stock_datetime
        rows.append(
            _txn(
                stock,
                TXN_RECEIVED,
                dt,
                actor=actor,
                qty_delta=Decimal("1"),
                unit_qty_delta=stock.container_unit_qty or Decimal("0"),
            )
        )

    # ALLOCATED
    if allocation is not None:
        rows.append(
            _txn(
                stock,
                TXN_ALLOCATED,
                allocation.allocation_datetime,
                actor=actor,
                to_allocation=allocation,
            )
        )

    # TRANSFER_DISPATCHED — one row per transfer (stock may have been transferred
    # more than once, e.g. central → site → central → site).
    for sti in stock.stocktransferitem_set.all():
        rows.append(
            _txn(
                stock,
                TXN_TRANSFER_DISPATCHED,
                sti.transfer_item_datetime,
                actor=actor,
                from_location_id=sti.stock_transfer.from_location_id,
                to_location_id=sti.stock_transfer.to_location_id,
                stock_transfer_item=sti,
                to_allocation=allocation,
            )
        )

    # TRANSFER_RECEIVED
    try:
        cali: ConfirmationAtLocationItem = stock.confirmationatlocationitem
        rows.append(
            _txn(
                stock,
                TXN_TRANSFER_RECEIVED,
                cali.confirmed_datetime or cali.transfer_confirmation_item_datetime,
                actor=actor,
                to_location_id=cali.confirm_at_location.location_id,
                stock_transfer_item=cali.stock_transfer_item,
                to_allocation=allocation,
            )
        )
    except ConfirmationAtLocationItem.DoesNotExist:
        pass

    # STORED — current bin item or deleted bin item (historical record).
    # Fallback to stock_datetime if stored_at_location=True but no record survives.
    stored_dt = None
    try:
        sbi: StorageBinItem = stock.storagebinitem
        stored_dt = sbi.item_datetime
    except StorageBinItem.DoesNotExist:
        # May have been stored then deleted (e.g. after dispensing).
        hist = (
            StorageBinItem.history.filter(stock=stock, history_type="+")
            .order_by("history_date")
            .first()
        )
        if hist:
            stored_dt = hist.item_datetime
    if stored_dt is None and stock.stored_at_location:
        stored_dt = stock.stock_datetime
    if stored_dt is not None:
        rows.append(_txn(stock, TXN_STORED, stored_dt, actor=actor, to_allocation=allocation))

    # DISPENSED — also covers historical stocks where DispenseItem was deleted.
    has_dispense_item = False
    try:
        di: DispenseItem = stock.dispenseitem
        has_dispense_item = True
        rows.append(
            _txn(
                stock,
                TXN_DISPENSED,
                di.dispense_item_datetime,
                actor=actor,
                qty_delta=Decimal("-1"),
                unit_qty_delta=-(stock.container_unit_qty or Decimal("0")),
                dispense_item=di,
                from_allocation=allocation,
            )
        )
    except DispenseItem.DoesNotExist:
        pass
    if stock.dispensed and not has_dispense_item:
        rows.append(
            _txn(
                stock,
                TXN_DISPENSED,
                stock.stock_datetime,
                actor=actor,
                qty_delta=Decimal("-1"),
                unit_qty_delta=-(stock.container_unit_qty or Decimal("0")),
                from_allocation=allocation,
            )
        )

    # REPACK_CONSUMED — sum unit_qty_in across child stocks via the RepackRequest
    # bridge (repack_request__from_stock=stock).  This is more reliable than
    # filtering on Stock.from_stock directly: that FK may be NULL on older records
    # where the field was added after the repack was processed.
    consumed_unit_qty = (
                            Stock.objects.filter(repack_request__from_stock=stock)
                            .aggregate(total=Sum("unit_qty_in"))["total"]
                        ) or Decimal("0")
    if consumed_unit_qty > 0:
        # Prefer the user who processed the repack over the generic stock actor.
        # RepackRequest.user_modified is set by process_repack_request().
        repack_actor = actor
        rr = stock.repackrequest_set.order_by("-modified").first()
        if rr is not None:
            rr_username = getattr(rr, "user_modified", None) or getattr(rr, "user_created", None)
            if rr_username:
                repack_actor = _resolve_actor(rr_username, actor_cache) or actor
        rows.append(
            _txn(
                stock,
                TXN_REPACK_CONSUMED,
                stock.stock_datetime,
                actor=repack_actor,
                unit_qty_delta=-consumed_unit_qty,
            )
        )

    # Sort by datetime so the ledger reads chronologically.
    rows.sort(key=lambda r: r.transaction_datetime)
    return rows


class Command(BaseCommand):
    help = (
        "Back-fill StockTransaction rows for stock that pre-dates the "
        "transaction-log refactor. Safe to re-run: stocks that already "
        "have any StockTransaction rows are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Report what would be created without writing to the database.",
        )
        parser.add_argument(
            "--stock-code",
            type=str,
            default=None,
            help="Bootstrap a single stock code (useful for testing).",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        stock_code: str | None = options["stock_code"]

        qs = Stock.objects.filter(invalid_state=False).select_related(
            "current_allocation",
        ).prefetch_related(
            "stocktransferitem_set__stock_transfer",
            "confirmationatlocationitem",
            "storagebinitem",
            "dispenseitem",
        )

        if stock_code:
            qs = qs.filter(code=stock_code)

        already_have_txn = set(
            StockTransaction.objects.values_list("stock_id", flat=True).distinct()
        )
        # Stocks that already have TXN_RECEIVED specifically — used to
        # detect the case where a stock has other transactions but is missing
        # its RECEIVED row (created via live apply_transaction before bootstrap ran).
        already_have_received = set(
            StockTransaction.objects.filter(transaction_type=TXN_RECEIVED)
            .values_list("stock_id", flat=True)
            .distinct()
        )

        total = created_count = no_events = error_count = 0
        already_bootstrapped: list[str] = []
        stock_count = qs.count()
        actor_cache: dict = {}

        for stock in tqdm(qs.iterator(chunk_size=500), total=stock_count, unit="stock"):
            total += 1
            if stock.pk in already_have_txn:
                # Stock has some transactions — but check whether TXN_RECEIVED is
                # missing. This can happen when live apply_transaction calls (e.g.
                # TXN_STORED) ran before bootstrap, creating partial ledger entries
                # that caused bootstrap to skip the stock entirely on a previous run.
                if stock.confirmed and stock.pk not in already_have_received:
                    dt = stock.confirmed_datetime or stock.stock_datetime
                    actor = _resolve_actor(
                        stock.user_modified or stock.user_created, actor_cache
                    )
                    row = _txn(
                        stock,
                        TXN_RECEIVED,
                        dt,
                        actor=actor,
                        qty_delta=Decimal("1"),
                        unit_qty_delta=stock.container_unit_qty or Decimal("0"),
                    )
                    if not dry_run:
                        try:
                            with transaction.atomic():
                                StockTransaction.objects.bulk_create([row])
                            created_count += 1
                        except Exception as e:
                            error_count += 1
                            self.stderr.write(
                                self.style.ERROR(f"  {stock.code} (backfill RECEIVED): {e}")
                            )
                    else:
                        self.stdout.write(
                            f"  {stock.code}: {TXN_RECEIVED} @ {dt} [backfill]"
                        )
                        created_count += 1
                already_bootstrapped.append(stock.code)
                continue

            rows = _bootstrap_one(stock, actor_cache)
            if not rows:
                no_events += 1
                continue

            if dry_run:
                for row in rows:
                    self.stdout.write(
                        f"  {stock.code}: {row.transaction_type} @ {row.transaction_datetime}"
                    )
                created_count += len(rows)
            else:
                try:
                    with transaction.atomic():
                        StockTransaction.objects.bulk_create(rows)
                    created_count += len(rows)
                except Exception as e:
                    error_count += 1
                    self.stderr.write(self.style.ERROR(f"  {stock.code}: {e}"))

        label = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Processed {total} stocks: "
                f"{label} {created_count} transactions, "
                f"skipped {no_events} (no lifecycle events), "
                f"{len(already_bootstrapped)} already had transactions, "
                f"errors {error_count}."
            )
        )
        if already_bootstrapped:
            self.stdout.write("Stocks with existing transactions (skipped):")
            for code in sorted(already_bootstrapped):
                self.stdout.write(f"  {code}")
