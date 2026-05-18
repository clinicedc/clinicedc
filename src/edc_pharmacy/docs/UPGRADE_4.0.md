# Upgrading edc-pharmacy from 3.1.5 to 4.0.0

This guide is for **project developers and admins** maintaining a clinicedc-based EDC who are upgrading an existing deployment.

`edc-pharmacy` in 4.0.0 is a major refactor. The headline change is a new append-only transaction ledger (`StockTransaction`) plus a single `apply_transaction()` gateway. Every state transition on a `Stock` row — confirmed, allocated, transferred, stored, dispensed, returned, etc. — now flows through this gateway, which writes a ledger row and mutates the `Stock` cache columns under a sentinel. Several `post_save`/`post_delete` signal handlers that used to mutate cache columns implicitly have been **removed**; guarded fields on `Stock` will now raise `StockError` if mutated outside the gateway.

If you have **no custom code** importing from `edc_pharmacy` and **no custom signal listeners** that depend on its handlers, your upgrade is primarily a deployment-time data procedure (see § Deployment). Otherwise read all sections.

See also:
- `src/edc_pharmacy/docs/DESIGN_transaction_log.md` — architecture rationale
- `src/edc_pharmacy/docs/workflow.md` — operational flows

---

## TL;DR

After pulling 4.0.0, on every existing system run **in this exact order**:

```bash
uv run --dev manage.py migrate --settings=meta_edc.settings.debug && \
uv run --dev manage.py fix_historical_stock_state && \
uv run --dev manage.py bootstrap_stock_transactions && \
uv run --dev manage.py fix_historical_stock_state && \
uv run --dev manage.py check_stock_ledger
```

(Substitute your own `--settings=` module.)

The two `fix_historical_stock_state` runs are intentional: the first repairs cache columns inconsistent with the legacy state so that bootstrap has clean data to work from; the second patches the bootstrapped ledger rows themselves (a handful of location and qty-delta fixes only become resolvable after bootstrap has run). `check_stock_ledger` must exit 0 before the system is considered upgraded.

If your project imports any of the changed utils / views / models listed in § Breaking API changes, fix call sites before deploying.

---

## Deployment procedure

Run as the application user against the production database (after taking a backup).

```bash
uv run --dev manage.py migrate --settings=<your.settings>
uv run --dev manage.py fix_historical_stock_state
uv run --dev manage.py bootstrap_stock_transactions
uv run --dev manage.py fix_historical_stock_state
uv run --dev manage.py check_stock_ledger
```

What each step does:

| Step | Purpose |
|---|---|
| `migrate` | Applies migrations `0139`–`0157` (19 new migrations covering the new ledger, return workflow, allocation refactor, stock-take, etc.) |
| `fix_historical_stock_state` (first pass) | Repairs Stock cache columns where the legacy signal handlers left them inconsistent (e.g. `in_transit` stuck `True`, `allocation` not nulled after dispense, bulk stock at non-central location). Idempotent. |
| `bootstrap_stock_transactions` | Replays each Stock's lifecycle from the surviving model state and writes the corresponding `StockTransaction` rows. Skips stocks that already have ledger rows, so safe to re-run. |
| `fix_historical_stock_state` (second pass) | Now operates on the bootstrapped ledger rows themselves (`TXN_RECEIVED qty_delta=0` corrections, `from_location/to_location` patches for transactions captured with the wrong location). The first pass is a no-op for these fixes; the second is where they actually take effect. |
| `check_stock_ledger` | Replays each Stock's ledger and asserts the derived state matches its cached columns. Exits non-zero on any discrepancy. **Required gate.** |

Migration `0157_backfill_allocation_stock_backpointer` (run during `migrate`) populates the new `Allocation.stock` FK for legacy rows where it was left NULL by pre-4.0 `allocate_stock`. The same fix is also exposed via `fix_historical_stock_state` for rerunnability.

---

## Architectural changes

### 1. `StockTransaction` is now the authoritative ledger

In 3.1.5, `StockTransaction` was a near-empty stub and Stock state was set by mutating fields directly (often from signal handlers). In 4.0.0:

- Every state transition writes one `StockTransaction` row (append-only, never updated or deleted).
- `Stock`'s cached boolean columns (`confirmed`, `dispensed`, `in_transit`, etc.) are the balance sheet, derivable from the ledger by replay.
- `apply_transaction(stock, TXN_*, actor, **kwargs)` is the **only** legal path to change those columns.
- Direct `stock.<guarded_field> = ...; stock.save()` raises `StockError`.

The `StockTransaction` model now has rich fields: `transaction_type`, `actor`, `qty_delta`, `unit_qty_delta`, `from_/to_location`, `from_/to_allocation`, `from_/to_bin`, source FKs (`receive_item`, `repack_request`, `stock_transfer_item`, `dispense_item`, `return_item`), `reverses` self-FK, `state_after` JSONField, plus `HistoricalRecords()`.

### 2. Removed signal handlers (`models/signals.py`)

Custom code that registered listeners alongside these dispatch_uids, or that relied on the side effect of saving the named child object, must be migrated to use `apply_transaction()` or to listen on `StockTransaction.post_save` instead.

| Removed `dispatch_uid` | What it used to do |
|---|---|
| `confirmation_on_post_save` | Set `Stock.confirmed=True` when a `Confirmation` was saved |
| `confirmation_on_post_delete` | Reverted `Confirmation` save |
| `stock_adjustment_on_post_save` | Pushed `unit_qty_in_new` into `Stock.unit_qty_in`; raised `InsufficientStockError` |
| `allocation_on_post_save` | Copied `subject_identifier` from `Allocation` to `Stock` |
| `allocation_post_delete` | Reset `Stock.subject_identifier` and `Stock.allocation` |
| `stock_transfer_item_on_post_save` | Set `Stock.in_transit=True` |
| `stock_transfer_item_post_delete` | Set `Stock.in_transit=False` |
| `confirm_at_location_item_on_post_save` | Set `Stock.confirmed_at_location=True` |
| `confirm_at_location_item_post_delete` | Set `Stock.confirmed_at_location=False` |
| `storage_bin_item_on_post_save` | Set `Stock.stored_at_location=True` |
| `storage_bin_item_post_delete` | Set `Stock.stored_at_location=False` |
| `dispense_item_on_post_save` | Set `Stock.dispensed=True`, `qty_out=1`, deleted `StorageBinItem` |
| `dispense_item_on_post_delete` | Reverted dispense flags |

`allocation_pre_delete` is retained. `order_item_on_post_delete` was added to keep `Order.item_count` in sync.

### 3. Guarded fields on `Stock`

The following `Stock` fields are now guarded — mutation outside `apply_transaction()` raises `StockError`:

```
confirmed, confirmed_at_location, in_transit, stored_at_location,
dispensed, destroyed, return_requested, quarantined, damaged, lost,
expired, voided, subject_identifier, allocation_id
```

The guard is enforced by a thread-local sentinel set by `apply_delta_context()` and checked in `Stock.save()`. Tests that mutate these fields for setup must wrap the mutation in `apply_delta_context()` or use `apply_transaction()`.

### 4. `Stock.allocation` is now a sticky `ForeignKey` (was `OneToOneField`)

`Stock.allocation` is preserved across dispense, damage, destroy, expire, lose, void, quarantine, etc. — it is cleared **only** when `TXN_RETURN_DISPOSITION_REPOOLED` runs. An `Allocation` is considered active when `Allocation.ended_datetime IS NULL`.

Custom code that previously checked `stock.allocation is None` to detect a dispensed stock must instead check:

```python
if stock.allocation and stock.allocation.ended_datetime is None:
    # active allocation
```

Or use the helper status flags on `Stock` itself.

Partial unique constraint `one_active_allocation_per_stock` enforces: at most one `Allocation` per `Stock` with `ended_datetime IS NULL`. Run `manage.py check_allocation_invariant` if you suspect legacy data violates this.

`Allocation` gained the back-pointer `stock` FK plus `started_datetime`, `ended_datetime`, `ended_reason`.

---

## Breaking API changes

### Utils

| Function | Change |
|---|---|
| `utils.dispense.dispense` | **Return type changed.** Was `QuerySet[DispenseItem] \| None`; now `tuple[list[str], list[str], list[str]]` = `(dispensed, already_dispensed, invalid)`. Whole-batch abort on subject/site/unallocated safety violations. |
| `utils.confirm_stock.confirm_stock` | Adds `actor: AbstractUser \| None = None` (kwarg). |
| `utils.allocate_stock.allocate_stock` | Adds `actor: AbstractUser \| None = None` (kwarg). |
| `utils.confirm_stock_at_location.confirm_stock_at_location` | Signature unchanged; internally rewritten to use `apply_transaction(TXN_TRANSFER_RECEIVED)`. Returns `(confirmed, already_confirmed, invalid)`. |
| `utils.transfer_stock_to_location.transfer_stock_to_location` | Signature unchanged; internally rewritten to use `apply_transaction(TXN_TRANSFER_DISPATCHED)`. |
| `utils.process_repack_request.process_repack_request` | **`repack_request_id` and `username` are now required positional arguments** (were optional in 3.1.5). |

### Views

| View / function | Change |
|---|---|
| `views.add_to_storage_bin_view.update_bin` | **Return type changed** from 2-tuple `(created, not_created)` to 3-tuple `(created, already_stored, invalid)`. Signature: `user_created`/`created` removed; `actor: AbstractUser \| None = None` added. |
| `views.move_to_storage_bin_view.move_to_bin` | Now goes through `apply_transaction(TXN_BIN_MOVED, …)`. Signature: `user_modified: str` → `actor: AbstractUser`. |
| `DispenseView.post` | Now unpacks the new tuple-of-lists return shape of `dispense()`. |
| `AddToStorageBinView.post` / `MoveToStorageBinView.post` | Pre-existing bug fixed: `redirect_on_*` guard helper return values are now honored — those redirects now actually fire. |
| `AllocateToSubjectView` | Redirect URL no longer carries `?q=` filter. |

### New API: `transaction_log` package

```python
from edc_pharmacy.transaction_log import apply_transaction, compute_delta
from edc_pharmacy.transaction_log import CurrentState, StateDelta
from edc_pharmacy.transaction_log import apply_delta_context, is_apply_delta_active
```

- `apply_transaction(stock, txn_type, actor, *, reason="", **kwargs) -> StockTransaction` — single gateway. Acquires `select_for_update` on `stock`, runs `compute_delta`, raises `InvalidTransitionError` on precondition failure, otherwise mutates Stock + writes the ledger row in one atomic.
- `compute_delta(txn_type, current_state, **kwargs) -> StateDelta` — pure function; no side effects.
- `apply_delta_context()` — context manager that opens the sentinel; only code running inside it may write guarded fields.

---

## New models

| Model | Purpose |
|---|---|
| `ReturnRequest` | Site → central return manifest. Fields: `return_identifier`, `return_datetime`, `from_location`, `to_location`, `item_count`, `comment`, `cancel`. |
| `ReturnItem` | One stock item in a `ReturnRequest`. `stock` FK is limited to `return_requested=True`. |
| `StockTake` | Stock-take event for a bin. Tracks `expected_count`, `scanned_count`, `matched_count`, `missing_count`, `unexpected_count`, `status`. |
| `StockTakeItem` | Per-code outcome row of a stock-take. `status` ∈ {`MATCHED`, `MISSING`, `UNEXPECTED`}. |

Removed:

| Model | Replacement |
|---|---|
| `StockAdjustment` | The model is gone (migration 0152). Adjustments are now a view-driven action that calls `apply_transaction(TXN_ADJUSTED \| TXN_DAMAGED \| TXN_EXPIRED \| TXN_LOST \| TXN_VOIDED, …)`. The `StockAdjustmentView` remains as the UI entry point. |
| `StockTransactionType` | Replaced by `STOCK_TRANSACTION_CHOICES` (CharField choices) — no list model to manage. |

Other model field changes:

- `Order.sent` removed → replaced by `printed`, `printed_datetime`, `printed_by`.
- `Order.item_count` default `0` (was nullable, `MinValueValidator(1)` → `MinValueValidator(0)`).
- `OrderItem.unit_qty_ordered`/`_received`/`_pending` default `Decimal("0.0")` (were nullable).
- `Stock` gained guarded boolean fields: `return_requested`, `quarantined`, `damaged`, `lost`, `expired`, `voided`.
- `StockRequest` gained M2M `visit_schedules` → `edc_visit_schedule.VisitScheduleSummary`.

---

## New TXN constants (`constants.py`)

```
TXN_RECEIVED, TXN_ALLOCATED, TXN_ALLOCATION_ENDED,
TXN_TRANSFER_DISPATCHED, TXN_TRANSFER_RECEIVED,
TXN_STORED, TXN_BIN_MOVED,
TXN_REPACK_CONSUMED, TXN_REPACK_PRODUCED,
TXN_DISPENSED,
TXN_RETURN_REQUESTED, TXN_RETURN_DISPATCHED, TXN_RETURN_RECEIVED,
TXN_RETURN_DISPOSITION_REPOOLED,
TXN_RETURN_DISPOSITION_QUARANTINED,
TXN_RETURN_DISPOSITION_DESTROYED,
TXN_ADJUSTED, TXN_DAMAGED, TXN_LOST, TXN_EXPIRED, TXN_VOIDED,
TXN_REVERSAL,
ALLOCATION_END_REASONS  # frozenset of legal Allocation.ended_reason values
```

Removed: `PARTIAL` (now imported from `clinicedc_constants`).

New exceptions in `exceptions.py`: `ReturnError`, `InvalidTransitionError`.

---

## New management commands

| Command | Purpose |
|---|---|
| `bootstrap_stock_transactions` | Back-fill `StockTransaction` rows for legacy stocks. Idempotent. |
| `fix_historical_stock_state` | One-time (rerunnable) data fix for cache columns inconsistent with the ledger. 11 distinct fixes documented in the command's module docstring. |
| `check_stock_ledger` | Replay each Stock's ledger; assert cache columns match. Non-zero exit on discrepancy. **Run as a deploy gate.** |
| `check_allocation_invariant` | Verify the Stock ↔ Allocation sticky-pointer invariants. |
| `fix_order_item_qty_pending` | Recompute `OrderItem.unit_qty_received`/`_pending` and `Order.status` from `ReceiveItem` rows. |

---

## New utils (returns workflow)

```python
from edc_pharmacy.utils import (
    request_stock_return,   # → TXN_RETURN_REQUESTED
    dispatch_return,        # → TXN_RETURN_DISPATCHED
    receive_return,         # → TXN_RETURN_RECEIVED
    disposition_return,     # → TXN_RETURN_DISPOSITION_{REPOOLED,QUARANTINED,DESTROYED}
)
```

All four return `(processed_codes, skipped_codes)` two-tuples. `InvalidTransitionError` from any underlying `apply_transaction` call is caught and the offending code is added to `skipped` with the error message.

---

## New views and URLs

The pharmacy UI was substantially expanded. New view classes (selection):

- Order: `OrderHomeView`, `OrderView`, `OrderEditView`, `OrderItemEditView`
- Receive: `ReceiveHomeView`, `ReceiveOrderView`, `ReceiveOrderEditView`, `ReceiveOrderItemView`, `ReceiveLotAddView`, `ReceiveSupplierAddView`/`ReceiveSupplierEditView`, `ReceiveStockListView`, `ReceiveEditView`
- Repack: `RepackHomeView`, `RepackView`, `RepackEditView`
- Stock request: `StockRequestHomeView`, `StockRequestView`, `StockRequestEditView`
- Stock transfer: `StockTransferHomeView`, `StockTransferEditView`
- Returns: `ReturnCentralView`, `ReturnRequestView`, `ReturnReceiveView`, `ReturnDispositionView`
- Stock-take: `StockTakeHomeView`, `StockTakeScanView`, `StockTakeResultsView`, `StockTakeDiscrepancyReportView`, `print_stock_take_discrepancy_report_view`
- Ledger viewer: `LedgerView`
- Reports: `BulkStockReportView`, `SiteStockReportView`, `ContainerBalanceReportView`, `LotStockListView`
- PDFs: `print_order_view`, `print_return_manifest_view`, `print_bin_labels_view`

All have corresponding URL patterns added in `urls.py`.

---

## Admin changes

| Admin | Change |
|---|---|
| `StockAdjustmentAdmin` | Removed (model gone). |
| `ReturnRequestAdmin`, `ReturnItemAdmin` | Added. |
| `StockTakeAdmin` | Added. |
| `StockTransactionAdmin` | Added — ledger browser with import-export resource. |
| `StockAdmin` | Columns `formatted_confirmed/_allocation/_transferred/_confirmed_at_location/_dispensed` removed; replaced by a single `lifecycle_stage` badge column and `last_transaction`. New filters: `StageListFilter`, `status`, `invalid_state`. `get_queryset` now prefetches `transactions`. |
| New action | `print_return_manifest_action` in `admin/actions/print_return_manifest.py` |

---

## Forms

New form modules under `forms/stock/`: `lot_add_form`, `order_edit_form`, `order_item_add_form`, `receive_header_form`, `receive_item_add_form`, `repack_edit_form`, `stock_request_edit_form`, `stock_transfer_edit_form`, `supplier_add_form`. Projects that override pharmacy forms should check their overrides against these.

---

## What custom code probably needs to change

A quick checklist for each consumer:

- [ ] Anywhere you call `dispense(...)` — unpack the new 3-tuple return value.
- [ ] Anywhere you call `update_bin(...)` — unpack the new 3-tuple return value; drop `user_created`/`created` kwargs and pass `actor=request.user`.
- [ ] Anywhere you call `move_to_bin(...)` — pass `actor=request.user` instead of `request.user.username`.
- [ ] Anywhere you call `confirm_stock(...)` / `allocate_stock(...)` — pass an `actor=` kwarg.
- [ ] Anywhere you call `process_repack_request(...)` — supply both `repack_request_id` and `username` as positional/required args.
- [ ] Anywhere you mutate `Stock.confirmed`/`Stock.dispensed`/`Stock.in_transit`/etc. directly — call `apply_transaction()` instead, or wrap the mutation in `apply_delta_context()` if you have a very good reason (typically test setup only).
- [ ] Anywhere you check `stock.allocation is None` to detect a dispensed stock — check `stock.allocation.ended_datetime is not None` instead, or use `stock.dispensed`.
- [ ] Anywhere you registered a `post_save` listener on `Confirmation` / `DispenseItem` / `StorageBinItem` / `ConfirmationAtLocationItem` / `StockTransferItem` / `Allocation` / `StockAdjustment` expecting the pharmacy handler to fire first — that handler is gone. Listen on `StockTransaction.post_save` if you need to react to state changes.
- [ ] Any code importing `StockAdjustment` (model) — gone. The view + TXN-typed adjustments replace it.
- [ ] Any code importing `StockTransactionType` (model) — gone. Use `STOCK_TRANSACTION_CHOICES` from `choices.py`.
- [ ] Migration `0157_backfill_allocation_stock_backpointer` runs once at deploy. If you skipped it for some reason, run `manage.py fix_historical_stock_state` to backfill.

---

## Verification

A successful upgrade exits cleanly from:

```bash
uv run --dev manage.py check_stock_ledger
```

If discrepancies are reported, the most common causes are:

1. `fix_historical_stock_state` wasn't run a second time after bootstrap.
2. Custom code wrote to a Stock field directly while the upgrade procedure was running, racing with `bootstrap_stock_transactions`. Re-run `bootstrap_stock_transactions` for the offending codes only (`--stock-code <code>`) after fixing the offending writer.
3. An `Allocation` with `stock_id IS NULL` survived. Run `manage.py fix_historical_stock_state` again.

For deeper diagnostics, run `check_stock_ledger --stock-code <code>` to see the per-field discrepancy report for a single stock.
