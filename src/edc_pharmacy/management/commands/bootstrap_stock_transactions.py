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
    uv --nodev --no-sources manage.py shell -c \
        "from edc_pharmacy.models import StockTransaction; \
        StockTransaction.objects.all().delete()"
    uv --nodev --no-sources manage.py bootstrap_stock_transactions
`   uv --nodev --no-sources manage.py check_stock_ledger
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from django.db.models import Sum
from tqdm import tqdm

from ...constants import (
    TXN_ALLOCATED,
    TXN_DISPENSED,
    TXN_RECEIVED,
    TXN_REPACK_CONSUMED,
    TXN_STORED,
    TXN_TRANSFER_DISPATCHED,
    TXN_TRANSFER_RECEIVED,
)
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
        user_cls = get_user_model()
        try:
            cache[username] = user_cls.objects.get(username=username)
        except user_cls.DoesNotExist:
            cache[username] = None
    return cache[username]


def _txn(
    stock: Stock,
    txn_type: str,
    dt,
    *,
    actor=None,
    username: str = "",
    from_location_id=None,
    to_location_id=None,
    qty_delta: Decimal = Decimal(0),
    unit_qty_delta: Decimal = Decimal(0),
    **fk_kwargs,
) -> StockTransaction:
    # Use the explicit username string when provided (even if actor is None
    # because the User account no longer exists in the DB).
    effective_username = username or (actor.username if actor else "")
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
        user_created=effective_username,
        user_modified=effective_username,
        **fk_kwargs,
    )


def bootstrap_one(stock: Stock, actor_cache: dict) -> list[StockTransaction]:
    """Return unsaved StockTransaction instances for a single stock."""
    rows: list[StockTransaction] = []

    # raw_username is the string stored on the model — kept even when the User
    # account no longer exists so that user_created/user_modified are populated.
    raw_username = stock.user_modified or stock.user_created or ""
    actor = _resolve_actor(raw_username, actor_cache)

    def t(txn_type: str, dt, *, actor=actor, username=raw_username, **kw):
        """Shorthand: call _txn with stock, raw_username and defaults bound."""
        return _txn(stock, txn_type, dt, actor=actor, username=username, **kw)

    # Resolve allocation — stock.allocation is None for dispensed/ended stocks,
    # but Allocation.code == stock.code so the record is still recoverable.
    allocation = stock.allocation or Allocation.objects.filter(code=stock.code).first()

    # RECEIVED — qty_in=+1, unit_qty_in=+container_unit_qty.
    rows = bootstrap_received(rows, stock, t)

    # ALLOCATED
    rows = bootstrap_allocated(rows, stock, allocation, t)

    # TRANSFER_DISPATCHED — one row per transfer (stock may have been transferred
    # more than once, e.g. central → site → central → site).
    rows = bootstrap_transfer_dispatch(rows, stock, allocation, t)

    # TRANSFER_RECEIVED
    rows = bootstrap_transfer_received(rows, stock, allocation, t)

    # STORED — current bin item or deleted bin item (historical record).
    # Fallback to stock_datetime if stored_at_location=True but no record survives.
    rows = bootstrap_stored(rows, stock, allocation, t)

    # DISPENSED — also covers historical stocks where DispenseItem was deleted.
    rows = bootstrap_dispensed(rows, stock, allocation, t)

    # REPACK_CONSUMED — sum unit_qty_in across child stocks via the RepackRequest
    # bridge (repack_request__from_stock=stock).  This is more reliable than
    # filtering on Stock.from_stock directly: that FK may be NULL on older records
    # where the field was added after the repack was processed.
    rows = bootstrap_repack(rows, stock, raw_username, actor, actor_cache, t)

    # Sort by datetime so the ledger reads chronologically.
    rows.sort(key=lambda r: r.transaction_datetime)
    return rows


def bootstrap_received(
    rows: list[StockTransaction], stock: Stock, t: Callable
) -> list[StockTransaction]:
    if stock.confirmed:
        dt = stock.confirmed_datetime or stock.stock_datetime
        rows.append(
            t(
                TXN_RECEIVED,
                dt,
                qty_delta=Decimal(1),
                unit_qty_delta=stock.container_unit_qty or Decimal(0),
                receive_item=stock.receive_item,
            )
        )
    return rows


def bootstrap_allocated(
    rows: list[StockTransaction], stock: Stock, allocation: Allocation | None, t: Callable
) -> list[StockTransaction]:
    if allocation is not None:
        rows.append(
            t(
                TXN_ALLOCATED,
                allocation.allocation_datetime,
                to_allocation=allocation,
                receive_item=stock.receive_item,
            )
        )
    return rows


def bootstrap_transfer_dispatch(
    rows: list[StockTransaction], stock: Stock, allocation: Allocation, t: Callable
) -> list[StockTransaction]:
    for obj in stock.stocktransferitem_set.all():
        rows.append(  # noqa: PERF401
            t(
                TXN_TRANSFER_DISPATCHED,
                obj.transfer_item_datetime,
                from_location_id=obj.stock_transfer.from_location_id,
                to_location_id=obj.stock_transfer.to_location_id,
                stock_transfer_item=obj,
                to_allocation=allocation,
                receive_item=stock.receive_item,
            )
        )
    return rows


def bootstrap_transfer_received(
    rows: list[StockTransaction], stock: Stock, allocation: Allocation, t: Callable
) -> list[StockTransaction]:
    try:
        obj: ConfirmationAtLocationItem = stock.confirmationatlocationitem
        rows.append(
            t(
                TXN_TRANSFER_RECEIVED,
                obj.confirmed_datetime or obj.transfer_confirmation_item_datetime,
                to_location_id=obj.confirm_at_location.location_id,
                stock_transfer_item=obj.stock_transfer_item,
                to_allocation=allocation,
                receive_item=stock.receive_item,
            )
        )
    except ConfirmationAtLocationItem.DoesNotExist:
        pass
    return rows


def bootstrap_stored(
    rows: list[StockTransaction], stock: Stock, allocation: Allocation, t: Callable
) -> list[StockTransaction]:
    sbi = None
    stored_dt = None
    try:
        sbi: StorageBinItem = stock.storagebinitem
    except StorageBinItem.DoesNotExist:
        # May have been stored then deleted (e.g. after dispensing).
        hist = (
            StorageBinItem.history.filter(stock=stock, history_type="+")
            .order_by("history_date")
            .first()
        )
        if hist:
            stored_dt = hist.item_datetime
    else:
        stored_dt = sbi.item_datetime
    if stored_dt is None and stock.stored_at_location:
        stored_dt = stock.stock_datetime
    if stored_dt is not None:
        rows.append(
            t(
                TXN_STORED,
                stored_dt,
                to_allocation=allocation,
                receive_item=stock.receive_item,
                to_bin=getattr(sbi, "storage_bin", None),
            )
        )
    return rows


def bootstrap_dispensed(
    rows: list[StockTransaction], stock: Stock, allocation: Allocation, t: Callable
) -> list[StockTransaction]:
    has_dispense_item = False
    try:
        di: DispenseItem = stock.dispenseitem
    except DispenseItem.DoesNotExist:
        pass
    else:
        has_dispense_item = True
        rows.append(
            t(
                TXN_DISPENSED,
                di.dispense_item_datetime,
                qty_delta=Decimal(-1),
                unit_qty_delta=-(stock.container_unit_qty or Decimal(0)),
                dispense_item=di,
                from_allocation=allocation,
                receive_item=stock.receive_item,
            )
        )

    if stock.dispensed and not has_dispense_item:
        rows.append(
            t(
                TXN_DISPENSED,
                stock.stock_datetime,
                qty_delta=Decimal(-1),
                unit_qty_delta=-(stock.container_unit_qty or Decimal(0)),
                from_allocation=allocation,
            )
        )
    return rows


def bootstrap_repack(
    rows: list[StockTransaction],
    stock: Stock,
    raw_username: str | None,
    actor,
    actor_cache,
    t: Callable,
) -> list[StockTransaction]:
    consumed_unit_qty = (
        Stock.objects.filter(repack_request__from_stock=stock).aggregate(
            total=Sum("unit_qty_in")
        )["total"]
    ) or Decimal(0)
    if consumed_unit_qty > 0:
        # Prefer the user who processed the repack over the generic stock actor.
        # RepackRequest.user_modified is set by process_repack_request().
        rr = stock.repack_requests.order_by("-modified").first()
        rr_raw = ""
        rr_actor = actor
        repack_dt = stock.stock_datetime
        if rr is not None:
            rr_raw = getattr(rr, "user_modified", "") or getattr(rr, "user_created", "") or ""
            if rr_raw:
                rr_actor = _resolve_actor(rr_raw, actor_cache) or actor
            repack_dt = rr.repack_datetime or stock.stock_datetime
        rows.append(
            t(
                TXN_REPACK_CONSUMED,
                repack_dt,
                actor=rr_actor,
                username=rr_raw or raw_username,
                unit_qty_delta=-consumed_unit_qty,
                receive_item=stock.receive_item,
                repack_request=rr,
            )
        )
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

    def handle(self, *args, **options):  # noqa: ARG002
        dry_run: bool = options["dry_run"]
        stock_code: str | None = options["stock_code"]

        qs = (
            Stock.objects.filter(invalid_state=False)
            .select_related(
                "allocation",
            )
            .prefetch_related(
                "stocktransferitem_set__stock_transfer",
                "confirmationatlocationitem",
                "storagebinitem",
                "dispenseitem",
            )
        )

        if stock_code:
            qs = qs.filter(code=stock_code)

        total = created_count = no_events = error_count = 0
        already_bootstrapped: list[str] = []
        skipped_deleted: list[str] = []
        stock_count = qs.count()
        actor_cache: dict = {}

        for stock in tqdm(qs.iterator(chunk_size=500), total=stock_count, unit="stock"):
            total += 1
            try:
                with transaction.atomic():
                    # Lock this stock row
                    Stock.objects.select_for_update().get(pk=stock.pk)
                    # Re-check at DB level under the lock
                    if StockTransaction.objects.filter(stock_id=stock.pk).exists():
                        already_bootstrapped.append(stock.code)
                        continue
                    rows = bootstrap_one(stock, actor_cache)
                    if not rows:
                        no_events += 1
                        continue
                    if not dry_run:
                        StockTransaction.objects.bulk_create(rows)
                    created_count += len(rows)
            except Stock.DoesNotExist:
                # Deleted between iterator load and lock — skip silently.
                skipped_deleted += 1
            except DatabaseError as e:
                # IntegrityError, OperationalError (lock timeout/deadlock), etc.
                error_count += 1
                self.stderr.write(self.style.ERROR(f"  {stock.code}: {e}"))

        label = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Processed {total} stock records: "
                f"{label} {created_count} transactions, "
                f"skipped {no_events} (no lifecycle events), "
                f"{len(already_bootstrapped)} already had transactions, "
                f"{len(skipped_deleted)} stock skipped (deleted between lock), "
                f"errors {error_count}."
            )
        )
        if already_bootstrapped:
            self.stdout.write("Stocks with existing transactions (skipped):")
            for code in sorted(already_bootstrapped):
                self.stdout.write(f"  {code}")
