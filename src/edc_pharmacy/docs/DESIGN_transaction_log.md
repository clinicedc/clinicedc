# edc_pharmacy transaction-log refactor — design sketch

**Status:** Draft. Not implemented. Open for review.
**Audience:** edc_pharmacy maintainers.
**Author:** Erik van Widenfelt
**Related:** returns workflow, allocation history, dormant `StockTransaction` model.

---

## 1. Why

`Stock` today carries current state as boolean flags (`confirmed`,
`confirmed_at_location`, `stored_at_location`, `dispensed`, `destroyed`,
`in_transit`) plus the presence/absence of OneToOne child rows
(`StorageBinItem`, `ConfirmationAtLocationItem`, `DispenseItem`,
`Confirmation`, `Allocation`). Writes are driven by a dozen `post_save` /
`post_delete` signal handlers — each flipping one flag from a different
sender model.

That design is optimised for the forward monotonic path
(receive → repack → allocate → transfer → confirm → store → dispense). It
does not accommodate:

- **Returns** — bottle goes back from site to central, then is re-pooled,
  quarantined, or destroyed. Reversing booleans overloads their meaning.
- **Reallocation** — `Stock.allocation` is OneToOne, so a returned bottle
  cannot be allocated to a second subject while preserving history.
- **History** — only `HistoricalRecords` captures prior states, which is
  fine for audit trails but useless for answering "when was this bottle
  dispensed?" or "how long between receipt at site and storage?"

The dormant `StockTransaction` model already exists in the schema,
suggesting the original author anticipated this.

---

## 2. Target architecture — hybrid CQRS-lite

Keep the cache columns on `Stock` as a denormalised **state projection**
(balance sheet). Add the ledger rows (`StockTransaction`) as the **source
of truth for history** (general ledger). One write path enforces
consistency.

```
                ┌──────────────────────┐
   business ──> │  apply_transaction() │ ──> writes ledger row
   action       │   (choke point)      │ ──> writes cache columns
                └──────────────────────┘         (Stock + children)
```

**Rule:** never edit the cache without writing to the ledger.
Enforced by deleting all existing mutation signal handlers and routing
every write through `apply_transaction`. A debug-only `post_save`
tripwire on Stock can log any mutation whose call stack doesn't include
`apply_transaction`.

---

## 3. The three pieces — `StateDelta`, `compute_delta`, `apply_transaction`

The core contract splits **pure computation** from **imperative apply**,
so V2's replay engine (needed for reversals) is mechanical.

### 3.1 `StateDelta` — value object

Pure, immutable, no DB. Encodes everything `apply_transaction` must do
after writing the ledger row.

```python
from dataclasses import dataclass, field
from typing import Any, Literal

ChildAction = Literal["create", "delete", "unchanged"]
AllocationAction = Literal["create", "end", "unchanged"]

@dataclass(frozen=True)
class StateDelta:
    # Stock cache column updates. Keys are Stock field names.
    # Values are the new values (not deltas). Empty dict = no change.
    stock_fields: dict[str, Any] = field(default_factory=dict)

    # OneToOne child rows. "create" means apply_delta materialises the
    # row using kwargs; "delete" removes the existing row; "unchanged"
    # leaves it alone. A transaction can touch multiple children (e.g.
    # DISPENSED also deletes StorageBinItem).
    storage_bin_item: ChildAction = "unchanged"
    confirmation_at_location_item: ChildAction = "unchanged"
    confirmation: ChildAction = "unchanged"
    dispense_item: ChildAction = "unchanged"

    # Allocation lifecycle. "create" opens a new Allocation;
    # "end" sets ended_datetime + ended_reason on the active one.
    allocation_action: AllocationAction = "unchanged"
    allocation_end_reason: str | None = None
    # Sticky-pointer policy (§5.6): Stock.allocation and Stock.subject_identifier
    # are preserved across most "end" actions (dispensed, damaged, destroyed,
    # quarantined, etc.) so the bottle keeps its link to the prior subject for
    # audit. Only set True for REPOOLED, where the bottle re-enters the pool
    # and must lose the prior subject reference.
    clear_allocation: bool = False

    # Location change (None = no change). Writes Stock.location plus
    # the ledger from_location/to_location.
    new_location_id: int | None = None

    # Qty changes (signed). None = no change.
    qty_delta: "Decimal | None" = None
    unit_qty_delta: "Decimal | None" = None

    # Guards. Non-empty = refuse to apply.
    preconditions_failed: tuple[str, ...] = ()
```

Notes:
- `stock_fields` is **absolute values**, not deltas, because boolean
  flips and FKs are not naturally delta-able. `qty_delta` /
  `unit_qty_delta` *are* signed deltas because they compose over a
  lifetime (received 60, dispensed 30, adjusted -5, balance 25).
- `preconditions_failed` means `compute_delta` noticed the state is
  illegal for this transaction type (e.g. DISPENSED on a bottle that
  isn't stored). `apply_transaction` raises before touching the DB.

### 3.2 `compute_delta` — pure

Signature:

```python
def compute_delta(
    txn_type: str,
    current: CurrentState,
    **kwargs,
) -> StateDelta: ...
```

`CurrentState` is a snapshot of what `compute_delta` needs to reason
about the stock row, read once by `apply_transaction` before the call:

```python
@dataclass(frozen=True)
class CurrentState:
    stock_id: int
    location_id: int | None
    confirmed: bool
    confirmed_at_location: bool
    stored_at_location: bool
    dispensed: bool
    destroyed: bool
    in_transit: bool
    qty_in: Decimal
    qty_out: Decimal
    unit_qty_in: Decimal
    unit_qty_out: Decimal
    has_active_allocation: bool
    active_allocation_subject: str  # "" if none
    has_storage_bin_item: bool
    has_confirmation_at_location_item: bool
```

No ORM inside `compute_delta`. No `self`. Just a dispatch table:

```python
_COMPUTERS: dict[str, Callable[..., StateDelta]] = {
    "RECEIVED": _compute_received,
    "ALLOCATED": _compute_allocated,
    "ALLOCATION_ENDED": _compute_allocation_ended,
    "TRANSFER_RECEIVED": _compute_transfer_received,
    "DISPENSED": _compute_dispensed,
    # ... 17 more
}
```

Each computer is a small pure function. Easily unit-testable by
parameterising current-state tuples.

### 3.3 `apply_transaction` — orchestrator

```python
def apply_transaction(
    stock: Stock,
    txn_type: str,
    actor: User,
    *,
    reason: str = "",
    source_object: models.Model | None = None,
    **kwargs,
) -> StockTransaction:
    current = _snapshot(stock)
    delta = compute_delta(txn_type, current, **kwargs)
    if delta.preconditions_failed:
        raise InvalidTransitionError(
            f"{txn_type} refused on stock={stock.code}: "
            f"{'; '.join(delta.preconditions_failed)}"
        )
    with transaction.atomic():
        txn = _write_ledger_row(
            stock=stock,
            txn_type=txn_type,
            delta=delta,
            actor=actor,
            reason=reason,
            source_object=source_object,
            **kwargs,
        )
        _apply_delta(stock, delta, txn=txn, **kwargs)
    return txn
```

`_apply_delta` is the only place that does ORM writes on Stock and its
OneToOne children. It uses `update_fields=` on `Stock.save()` so the
existing save() guards still apply — in fact those guards should be
rewritten to accept only calls that originate in `_apply_delta`
(checked via a thread-local sentinel, not inspection of call stack).

`_write_ledger_row` snapshots the *post-delta* state into
`StockTransaction.state_after` JSONField. Makes "why is this in this
state?" a single query.

---

## 4. Triggers — scan utils as the choke-point callers

A subset of transaction types are **scan-driven**: the trigger is not a
business-object `.save()` but a barcode being scanned through a
dedicated view or admin action that funnels into a per-list util. Those
utils are the natural callers of `apply_transaction`, one call per
scanned code.

| Transaction | Trigger surface | Existing util | Child row materialised |
|---|---|---|---|
| `RECEIVED` (received & repacked) | admin actions `confirm_repacked_stock_action` / `confirm_received_stock_action` → scan view `confirm_stock_from_queryset_view` | `utils/confirm_stock.py::confirm_stock` | `Confirmation` |
| `TRANSFER_RECEIVED` | scan view `confirm_at_location_view` | `utils/confirm_stock_at_location.py` | `ConfirmationAtLocationItem` |
| `STORED` | scan views `add_to_storage_bin_view` / `move_to_storage_bin_view` | (likely a util alongside the views) | `StorageBinItem` |
| `DISPENSED` | scan view `dispense_view` | `utils/dispense.py::dispense` | `DispenseItem` |
| `RETURN_DISPATCHED` / `RETURN_RECEIVED` | (future, mirrors above) | (future) | (future) |

Call shape for every scan-driven flow:

```
[admin action OR view POST]
   └─ util(stock_codes, ...)                # iterates the scan list
        └─ for code in stock_codes:
              try:
                  stock = Stock.objects.get(code=code, ...)
                  apply_transaction(stock, TXN, actor=request.user, ...)
                  confirmed.append(code)
              except Stock.DoesNotExist:
                  invalid.append(code)
              except InvalidTransitionError:        # already confirmed etc.
                  already_confirmed.append(code)
   ↳ returns (confirmed, already_confirmed, invalid)
```

Today these utils call `Confirmation.objects.create(stock=stock, ...)`
(etc.) directly, and rely on a `post_save` signal to flip the cache
flag. After the refactor the util drops the direct `.create(...)`; the
child row is materialised inside `_apply_delta` per
`StateDelta.<child_action>="create"`. The util's three-bucket return
value stays unchanged — `apply_transaction` raising
`InvalidTransitionError("already confirmed")` maps to the
`already_confirmed` bucket the existing views already render.

`ScanDuplicates` (the model behind `migrations/0057_scanduplicates.py`)
is orthogonal — it logs duplicate scan attempts at the surface layer
and is unaffected by this refactor.

The non-scan-driven transactions (`ALLOCATED`, `ALLOCATION_ENDED`,
`TRANSFER_DISPATCHED`, `BIN_MOVED`, the exception types `DAMAGED` /
`LOST` / `EXPIRED` / `VOIDED`, and `ADJUSTED`) are triggered by admin
actions or model saves where the operator records a fact; no physical
scan. Same `apply_transaction` choke point, just different caller.

---

## 5. Representative cases (5 of 22)

Enough to prove the shape. The remaining 17 are mechanical fill-in.

### 5.1 `RECEIVED` (scan-driven)

A bulk receipt's labels are scanned at central pharmacy via
`confirm_stock` after `ReceiveItem` rows already exist.

**Caller:** `utils/confirm_stock.py::confirm_stock`, looping over
`stock_codes`.

**Preconditions:** stock row exists (created by `ReceiveItem`); not
already confirmed.

```python
def _compute_received(current, *, confirmed_datetime, **_) -> StateDelta:
    if current.confirmed:
        return StateDelta(preconditions_failed=("already confirmed",))
    return StateDelta(
        stock_fields={
            "confirmed": True,
            "confirmed_datetime": confirmed_datetime,
        },
        confirmation="create",
        # Note: qty / unit_qty deltas already booked at ReceiveItem time.
        # RECEIVED here is the *label-confirmation* event, not the
        # quantity event. If we model qty as also gated on confirmation,
        # this is where qty_delta moves; keeping it on ReceiveItem for V1
        # to minimise churn. Open question.
    )
```

`_apply_delta` materialises the `Confirmation` row using the
`confirmed_by` and `confirmed_datetime` kwargs threaded through from
the util.

### 5.2 `ALLOCATED` (business-action-driven)

Central pharmacist allocates a prepared bottle to a subject (via a
stock request).

**Preconditions:** not dispensed, not destroyed, no active allocation.

```python
def _compute_allocated(current, *, stock_request_item, registered_subject, **_):
    fail = []
    if current.dispensed:
        fail.append("already dispensed")
    if current.destroyed:
        fail.append("destroyed")
    if current.has_active_allocation:
        fail.append("already allocated (end it first)")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={
            "subject_identifier": registered_subject.subject_identifier,
        },
        allocation_action="create",
    )
```

The actual `Allocation` row is created by `_apply_delta` using
`stock_request_item` + `registered_subject` kwargs. `_apply_delta`
also sets `Stock.allocation_id` to the new Allocation row (the sticky
pointer — see §5.6 and §11.5).

### 5.3 `ALLOCATION_ENDED` (business-action-driven)

Close out an allocation. Reasons: `dispensed`, `returned`,
`reallocated`, `damaged`, `expired`, `voided`, `lost`.

```python
VALID_END_REASONS = {
    "dispensed", "returned", "reallocated",
    "damaged", "expired", "voided", "lost",
}

def _compute_allocation_ended(current, *, reason, **_):
    if not current.has_active_allocation:
        return StateDelta(preconditions_failed=("no active allocation",))
    if reason not in VALID_END_REASONS:
        return StateDelta(preconditions_failed=(f"invalid reason: {reason}",))
    # Sticky-pointer policy (see §5.6): ending the allocation stamps the
    # Allocation row but does NOT clear Stock.allocation or subject_identifier.
    # Only RETURN_DISPOSITION_REPOOLED clears them. The sole forward path
    # that clears the FK is repool; everything else preserves the link
    # for audit/history.
    return StateDelta(
        allocation_action="end",
        allocation_end_reason=reason,
    )
```

### 5.4 `TRANSFER_RECEIVED` (scan-driven)

Bottle arrives at the site pharmacy after being dispatched from
central. Flips `in_transit` off and `confirmed_at_location` on.

**Caller:** `utils/confirm_stock_at_location.py`, looping over the
codes scanned from the `confirm_at_location_view` POST.

**Preconditions:** in transit; not already confirmed at this location.

```python
def _compute_transfer_received(current, *, site_location_id, **_):
    fail = []
    if not current.in_transit:
        fail.append("not in transit")
    if current.confirmed_at_location:
        fail.append("already confirmed at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={
            "in_transit": False,
            "confirmed_at_location": True,
        },
        confirmation_at_location_item="create",
        new_location_id=site_location_id,
    )
```

### 5.5 `DISPENSED` (scan-driven)

Patient receives the bottle. Ends the allocation (reason=dispensed) and
removes the StorageBinItem — currently done as an *accidental*
side-effect in `dispense_item_on_post_save`; made explicit here.

**Caller:** `utils/dispense.py::dispense`, looping over the bottle
codes scanned at handover.

```python
def _compute_dispensed(current, *, dispense_item, **_):
    fail = []
    if current.dispensed:
        fail.append("already dispensed")
    if not current.stored_at_location:
        fail.append("not stored at location")
    if not current.has_active_allocation:
        fail.append("no active allocation")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={
            "dispensed": True,
            "stored_at_location": False,
            # Stock.allocation and subject_identifier intentionally preserved
            # (sticky-pointer policy, §5.6): dispense is terminal, the
            # bottle's recipient is a permanent record. The Allocation row
            # is stamped (ended_datetime, ended_reason="dispensed") by the
            # "end" action below.
        },
        dispense_item="create",
        storage_bin_item="delete",
        allocation_action="end",
        allocation_end_reason="dispensed",
        qty_delta=-dispense_item.qty,
        unit_qty_delta=-(dispense_item.unit_qty),
    )
```

Note: this single `DISPENSED` call replaces what today takes
`dispense_item_on_post_save` + the implicit StorageBinItem deletion +
a separate Allocation end path (which doesn't exist today because
allocation is OneToOne — it just gets overwritten on reallocation,
losing history).

### 5.6 `Stock.allocation` and `Stock.subject_identifier` — sticky-pointer policy

**The rule.** Once `ALLOCATED` sets `Stock.allocation` and
`Stock.subject_identifier`, they are **sticky**: preserved across every
forward transaction for the bottle's entire life, with **one** exception
— `RETURN_DISPOSITION_REPOOLED`, the only forward path that returns the
bottle to the available pool.

The Allocation row itself is always stamped (`ended_datetime`,
`ended_reason`) when the allocation logically ends, regardless of
whether the FK on Stock is cleared. So the answer to *"is this bottle
currently active for a subject?"* is a join, not a single column read:

```python
stock.allocation_id is not None
    and stock.allocation.ended_datetime is None
```

This is what `update_status()` uses to decide between `ALLOCATED` /
`AVAILABLE` / `ZERO_ITEM`.

| Transaction | `Stock.allocation` after | `Stock.subject_identifier` after | `Allocation.ended_datetime` |
|---|---|---|---|
| `ALLOCATED` | set → new row | set | NULL |
| `TRANSFER_DISPATCHED` / `_RECEIVED` | unchanged | unchanged | unchanged |
| `STORED` / `BIN_MOVED` | unchanged | unchanged | unchanged |
| `RETURN_REQUESTED` / `_DISPATCHED` / `_RECEIVED` | unchanged | unchanged | unchanged |
| `DISPENSED` | **kept** | **kept** | stamped (reason=dispensed) |
| `DAMAGED` / `LOST` / `EXPIRED` / `VOIDED` | **kept** | **kept** | stamped (reason=*) |
| `RETURN_DISPOSITION_QUARANTINED` | **kept** | **kept** | stamped (reason=quarantined) |
| `RETURN_DISPOSITION_DESTROYED` | **kept** | **kept** | stamped (reason=destroyed) |
| `RETURN_DISPOSITION_REPOOLED` | **cleared** | **cleared** | stamped (reason=repooled) |
| `ALLOCATION_ENDED` (admin path) | kept | kept | stamped (any reason) |

**Why sticky everywhere except repool.** The bottle's link to the
subject it was allocated to is a permanent record of *intent and
custody*. Dispensed → patient has it. Damaged → bottle was meant for
that patient and is now gone. Destroyed → same. Quarantined → held but
still under that patient's name pending decision. Only repool means
"the bottle never reached the patient and is being returned to the
shared pool" — and only then must the prior subject reference be
severed so that the bottle does not drag a stale subject identifier
into a future `ALLOCATED`.

**Audit traceability.** Even after repool clears `Stock.allocation`,
the historical link survives via:

* `Allocation.objects.filter(stock=stock).order_by("started_datetime")`
  — the canonical history; one row per allocation lifecycle, each with
  `registered_subject` (FK, PROTECT) and `subject_identifier` cache.
* `StockTransaction` ledger rows — `from_allocation` / `to_allocation`
  FKs (PROTECT) on every relevant txn.
* `DispenseItem → Dispense` chain (independent of the Allocation chain).

`Stock.subject_identifier` is **not** an audit field — it is a denormalised
cache mirroring `Stock.allocation.registered_subject.subject_identifier`
for fast list-view display. Auditors must query `Allocation` /
`StockTransaction`.

### 5.7 Implementation — single flag drives the choke-point

`StateDelta` carries a single boolean `clear_allocation` (default
`False`). Only `_compute_return_disposition_repooled` sets it `True`.
`_apply_delta`'s `end` branch reads it:

```python
elif delta.allocation_action == "end":
    ending_allocation = stock.allocation
    if ending_allocation is not None:
        # Always stamp the Allocation row.
        Allocation.objects.filter(pk=ending_allocation.pk).update(
            ended_datetime=ended_datetime,
            ended_reason=ended_reason,
        )
    created_objects["from_allocation"] = ending_allocation
    if delta.clear_allocation:        # repool only
        stock.allocation = None
        stock.subject_identifier = ""
        update_fields.extend(["allocation", "subject_identifier"])
```

`_write_ledger_row` uses `delta.allocation_action == "end"` to decide
that the ledger row's `to_allocation` should be `None`, regardless of
whether the FK on Stock was cleared — semantically, no allocation is
*active* after an end.

### 5.8 Re-allocation precondition

`_compute_allocated` rejects any stock where `Stock.allocation` is
already set:

```python
if current_state.has_allocation:
    fail.append("stock still references a prior allocation — repool first")
```

The error message describes the new policy: a bottle whose allocation
has been ended must be repooled before it can be re-allocated. (Terminal
states — dispensed, damaged, destroyed, etc. — are blocked earlier by
`_check_not_terminal` and never reach this check.)

### 5.9 Call-site audit needed (separate task)

The rename `Stock.current_allocation → Stock.allocation` is mechanical.
The semantic shift to **sticky** is not — every place that reads
`Stock.allocation` (or filters `Stock` by `allocation__isnull`) and
treats it as "currently active" must be reviewed and, where appropriate,
also gate on `allocation__ended_datetime__isnull=True`.

Already updated in this change:

* `Stock.update_status()` — checks `ended_datetime is None`.
* `Stock.update_transferred()` — checks `ended_datetime is None`.
* `StockTransferItem.stock.limit_choices_to` — adds
  `allocation__ended_datetime__isnull=True`.

Sites that reference `Stock.allocation` and **must be reviewed** before
the policy goes live (non-exhaustive — grep `Stock.objects.filter(allocation__`):

* `admin/list_filters.py` — many `allocation__isnull` filters.
* `admin/stock/stock_proxy_admin.py` — `allocation__isnull=False`.
* `admin/stock/stock_transfer_item_admin.py` — `stock__allocation__isnull=False`.
* `admin/stock/stock_admin.py`, `stock_request_item_admin.py` —
  `obj.allocation.…` accesses are now safe (FK persists) but may
  display stale subject info on dispensed/damaged stock.
* `views/allocate_to_subject_view.py`, `views/print_labels_view.py`,
  `views/move_to_storage_bin_view.py`, `views/add_to_storage_bin_view.py`.
* `utils/allocate_stock.py`, `utils/confirmed_at_current_location.py`.
* `utils/dispense.py` — direct attribute access; safe but needs review.
* `analytics/dataframes/in_stock_for_subjects_df.py`.
* `pdf_reports/stock_pdf_report.py`.

Recommendation: add a manager helper to make the active-allocation
query a single, named call and migrate sites to it incrementally:

```python
class StockManager(models.Manager):
    def actively_allocated(self):
        return self.filter(allocation__isnull=False,
                           allocation__ended_datetime__isnull=True)
```

Note: many of the `__isnull` filters in the listing above are on
`StockRequestItem.allocation` (a different field — OneToOne from
`StockRequestItem` to `Allocation`). Those are unaffected by this
policy. The audit must distinguish `Stock.allocation` from
`StockRequestItem.allocation` per call site.

---

## 6. What goes away

Every mutation handler in `signals.py` listed in the code tour
(lines 73, 92, 211, 222, 235, 248, 261, 272, 320, 332, 342, 352, 362)
is deleted. The senders that drove those handlers (`Confirmation`,
`StockTransferItem`, `ConfirmationAtLocationItem`, `StorageBinItem`,
`DispenseItem`, `Allocation`, `StockAdjustment`) keep their `save()`
paths but no longer mutate `Stock` directly.

The replacement callers fall into two camps:

**Scan-driven** — utils that already exist and that already loop over
`stock_codes`. They drop the direct `child_row.objects.create(...)`
and instead call `apply_transaction(stock, TXN, ...)`, which
materialises the child row inside `_apply_delta`:

| Today | After |
|---|---|
| `confirm_stock` util `Confirmation.objects.create(stock=...)` → `confirmation_on_post_save` flips `stock.confirmed` | `confirm_stock` util calls `apply_transaction(stock, RECEIVED, confirmed_by=..., confirmed_datetime=...)` |
| `confirm_stock_at_location` util `ConfirmationAtLocationItem.objects.create(...)` → `confirm_at_location_item_on_post_save` flips `stock.confirmed_at_location` | util calls `apply_transaction(stock, TRANSFER_RECEIVED, location=...)` |
| `add_to_storage_bin` flow `StorageBinItem.objects.create(...)` → `storage_bin_item_on_post_save` flips `stock.stored_at_location` | call `apply_transaction(stock, STORED, bin=...)` |
| `dispense` util `DispenseItem.objects.create(...)` → `dispense_item_on_post_save` flips `stock.dispensed` and quietly deletes the StorageBinItem | util calls `apply_transaction(stock, DISPENSED, dispense_item_kwargs=...)`; the StorageBinItem deletion becomes an *explicit* `storage_bin_item="delete"` in `StateDelta` |

The earlier draft's claim that `ReceiveItem.save()` triggers `RECEIVED`
was wrong — `ReceiveItem` records *expected* receipt; the actual
confirmation event is the label scan that creates `Confirmation`.

**Business-action-driven** — admin actions or model saves where the
operator records a fact, no scan. These call `apply_transaction`
inline:

| Today | After |
|---|---|
| `transfer_stock` action / `transfer_stock_view` creates `StockTransferItem` → `stock_transfer_item_on_post_save` flips `in_transit` | action calls `apply_transaction(stock, TRANSFER_DISPATCHED, transfer_item=...)` |
| `allocate_stock` util writes `Allocation`; `allocation_on_post_save` denormalises `subject_identifier` | util calls `apply_transaction(stock, ALLOCATED, registered_subject=..., stock_request_item=...)` |
| `StockAdjustment.save()` → `stock_adjustment_on_post_save` mutates `unit_qty_in` | adjustment-creation path calls `apply_transaction(stock, ADJUSTED, unit_qty_in_new=...)` |

`Stock.save()`'s current mutation guards (lines 174–224) are
tightened: all mutation of guarded fields goes through `_apply_delta`,
which uses a thread-local sentinel so the save() guard can let
through only those writes. Any other save of a guarded field raises.

---

## 7. Testability payoff

- `compute_delta` is pure — every transaction type is a table test.
  Current-state in, expected StateDelta out. No DB, no fixtures.
- `apply_transaction` has one integration test per type that asserts
  ledger row written + cache matches.
- `check_stock_ledger` management command replays the log from
  `RECEIVED` and asserts the resulting projection equals the current
  cache. Catches any write that bypassed `apply_transaction`.

---

## 8. Not in this sketch (on purpose)

- Schema for expanded `StockTransaction` (defaults, indexes,
  constraints, `reverses` self-FK). See memory doc `project_edc_pharmacy_refactor.md`
  §"Expanded StockTransaction schema".
- Allocation OneToOne → FK migration. Same memory doc,
  §"Allocation model refactor".
- Bootstrap migration (synthesising historical ledger rows from existing
  timestamps). Next sketch (c).
- Stock schema changes (new cache flags: `return_requested`,
  `quarantined`). Next sketch (b).
- REVERSAL machinery. V2.

---

## 9. Open questions to settle before coding

1. **Thread-local vs call-stack sentinel** for Stock.save() guard — thread-local
   is simpler and faster, but risks silent leaks across requests if poorly
   scoped. Call-stack inspection is airtight but ugly. Recommend thread-local
   with an `apply_delta` context-manager that always clears on exit.

2. **`StockTransaction.state_after` JSONField** — redundant with replay. Worth
   the storage cost? Argument for: makes "why is this here" a single query;
   makes V2 reconciliation O(1) per row. Argument against: duplication,
   drift risk. Recommend keeping for V1; revisit.

3. **`source_object` as GenericFK vs separate nullable FKs per source
   model** — memory doc proposes separate FKs (`receive_item`, `repack_request`,
   `dispense_item`, etc.). That's more columns but better indexes and
   type safety. Sticking with separate FKs.

4. **`allocation_action = "end"` vs explicit `ALLOCATION_ENDED` as its own
   transaction type** — in the sketch above, `DISPENSED` directly sets
   `allocation_action="end"`. An alternative is: `DISPENSED` emits two ledger
   rows (`DISPENSED` + `ALLOCATION_ENDED`). Two rows is cleaner for the
   ledger but complicates `apply_transaction`'s single-row contract.
   Recommend: single row, `allocation_action` lives in the StateDelta,
   ledger records the effective end via `to_allocation` / `from_allocation`
   columns.

5. **Per-scan vs per-batch `transaction.atomic()`** — a scan session can be
   50+ bottles. Today's utils run each `child_row.objects.create(...)` inside
   the request transaction, so the whole batch is effectively one atomic
   block; if any single create fails, none commit. Two options after the
   refactor:

   - **Per-scan**: each `apply_transaction` opens its own `atomic()`. A
     mid-batch precondition failure (e.g. one already-confirmed code) does
     not roll back the bottles already confirmed in this session. Matches
     current user-visible behaviour where the view buckets results into
     confirmed / already_confirmed / invalid and shows a per-bottle summary.
   - **Per-batch**: the util wraps the whole `for code in stock_codes:` loop
     in one outer `atomic()`, and `apply_transaction` joins it (no nested
     atomic). One failed precondition still doesn't roll back the batch
     because preconditions raise before the DB writes; but a DB-level error
     (constraint violation in a child row create, deadlock) would now roll
     back the whole batch instead of just the offending bottle.

   Recommend per-scan. It matches today's three-bucket UX, isolates DB
   surprises to the offending row, and keeps batch sizes from blowing up
   long-running transactions on MySQL. The "all-or-nothing" semantics for a
   manifest aren't actually a requirement — the manifest is reconciled by
   the unconfirmed_count query, not by atomicity.

---

## 10. Next sketches

Per the memory doc's next-step list:

- **(b)** Stock schema changes — new cache flags, changed semantics,
  migration strategy for existing rows. → **§11 below.**
- **(c)** Bootstrap migration — synthesise historical `StockTransaction`
  rows from current data so projection equals replay on day one.

---

## 11. Sketch (b) — Stock schema changes

### 11.1 New cache flag columns

Six boolean flags to add (all `default=False`, `editable=False`):

| Field | Set by | Cleared by | Terminal? |
|---|---|---|---|
| `return_requested` | `RETURN_REQUESTED` | `RETURN_DISPATCHED` | No |
| `quarantined` | `RETURN_DISPOSITION_QUARANTINED` | `RETURN_DISPOSITION_REPOOLED` | No |
| `damaged` | `DAMAGED` | never | Soft — can subsequently be destroyed |
| `lost` | `LOST` | never | Yes |
| `expired` | `EXPIRED` | never | Yes |
| `voided` | `VOIDED` | never | Yes |

`destroyed` already exists on the model. Retain as-is.

Notes:
- `quarantined` is the only non-terminal new flag (besides `return_requested`).
  A quarantined bottle can be re-pooled: `RETURN_DISPOSITION_REPOOLED` clears
  the flag so "currently quarantined" stays a simple `filter(quarantined=True)`.
- `damaged` is soft-terminal: a damaged bottle can subsequently be destroyed
  (`damaged=True` AND `destroyed=True` is a valid state). All others
  (`lost`, `expired`, `voided`) are hard-terminal — once set, no further
  transitions in V1.
- `return_requested` is transient. It is cleared atomically by
  `RETURN_DISPATCHED`, which also sets `in_transit=True`. The two writes
  happen inside the single `_apply_delta` call — no intermediate state is
  ever visible.

### 11.2 Existing flag semantics (governance changes only)

No semantic change to the existing seven flags. What changes is *who sets
them*.

| Flag | Governed by today | Governed by after |
|---|---|---|
| `confirmed` | `confirmation_on_post_save` | `apply_transaction(RECEIVED, ...)` |
| `confirmed_at_location` | `confirm_at_location_item_on_post_save` | `apply_transaction(TRANSFER_RECEIVED, ...)` |
| `in_transit` | `stock_transfer_item_on_post_save` | `apply_transaction(TRANSFER_DISPATCHED / RECEIVED, ...)` |
| `stored_at_location` | `storage_bin_item_on_post_save` | `apply_transaction(STORED / DISPENSED / RETURN_DISPATCHED, ...)` |
| `dispensed` | `dispense_item_on_post_save` | `apply_transaction(DISPENSED, ...)` |
| `destroyed` | manual admin write (unguarded today) | `apply_transaction(RETURN_DISPOSITION_DESTROYED / DAMAGED+destroy, ...)` |

The `DISPENSED` path makes `stored_at_location=False` and `dispensed=True`
atomically — the old implicit side-effect in `dispense_item_on_post_save`
is now explicit in `StateDelta` (§5.5).

### 11.3 Illegal state combinations

These combinations must never exist. `apply_transaction` enforces them via
`compute_delta` preconditions; `check_stock_ledger` asserts them at audit
time.

```
# Terminal state exclusions (except damaged+destroyed, which is valid)
dispensed  + destroyed    dispensed + damaged      dispensed + lost
dispensed  + expired      dispensed + voided
lost       + destroyed    lost + expired           lost + voided
expired    + voided       voided + destroyed

# In-motion / storage exclusions
in_transit + stored_at_location
dispensed  + stored_at_location    dispensed + in_transit
destroyed  + in_transit
```

Encode as a `_check_not_terminal(current)` helper (returns a list of
failure strings) reused across all transaction computers that must refuse
to operate on a terminal bottle.

### 11.4 `Stock.save()` guard refactor

Today's guards use `update_fields` inspection — bypassed by any caller
that passes `update_fields=["in_transit"]` directly:

```python
# current — bypassable
if "in_transit" not in kwargs.get("update_fields", []):
    if self.in_transit != original.in_transit:
        raise StockError(...)
```

Replace with a thread-local sentinel:

```python
import threading
_tl = threading.local()

@contextmanager
def _apply_delta_context():
    _tl.active = True
    try:
        yield
    finally:
        _tl.active = False

GUARDED_FIELDS = frozenset({
    "confirmed", "confirmed_at_location", "in_transit",
    "stored_at_location", "dispensed", "destroyed",
    "return_requested", "quarantined",
    "damaged", "lost", "expired", "voided",
})
```

In `Stock.save()`, replace the three `update_fields` blocks with:

```python
if not getattr(_tl, "active", False):
    try:
        original = Stock.objects.get(pk=self.pk)
    except Stock.DoesNotExist:
        pass  # new row — nothing to guard
    else:
        changed = [f for f in GUARDED_FIELDS if getattr(self, f) != getattr(original, f)]
        if changed:
            raise StockError(
                f"Mutating {changed} requires apply_transaction. "
                "Do not write guarded fields directly."
            )
```

`_apply_delta` wraps all ORM writes inside `with _apply_delta_context():`.
Any path that mutates a guarded field without going through `_apply_delta`
trips the guard — including management commands, shell scripts, and test
fixtures that call `stock.save()` directly.

Three save()-time invariants that are NOT field mutations stay in `save()`:
- `stock_identifier` / `code` assignment (new row only — no guard needed).
- `verify_assignment_or_raise()` (lot/product consistency — always runs).
- `update_status()` (derived from `allocation` activeness, `qty_in`,
  `qty_out` — still recomputed on every save so it stays consistent when
  `_apply_delta` calls `stock.save()`). Active = `allocation_id IS NOT
  NULL AND allocation.ended_datetime IS NULL` (sticky-pointer policy, §5.6).

### 11.5 `allocation` OneToOne → `Stock.allocation` FK (sticky pointer)

Full 4-step migration sketch in the memory doc §"Allocation model
refactor". Summary for this doc:

- Remove: `allocation = OneToOneField(Allocation)` (the legacy reverse
  accessor on Stock from `Allocation.stock = OneToOneField`).
- Add: `allocation = FK(Allocation, null=True, on_delete=SET_NULL,
  related_name="+")` — the **sticky pointer** to the most recent
  Allocation for this Stock.

(An interim name `current_allocation` was used during the refactor; the
final field is named `allocation` because, under sticky-pointer policy,
the FK is preserved past dispense/damage/etc. — "current" is misleading.
The "currently active" sense is computed: `allocation IS NOT NULL AND
allocation.ended_datetime IS NULL`.)

`update_status()` and `verify_assignment_or_raise()` test
`self.allocation`. `update_status()` additionally checks
`self.allocation.ended_datetime is None` to distinguish active from
sticky-but-ended. The 4-step migration is independent of the boolean
flag changes and can land in a separate PR.

### 11.6 `status` field

`status` is computed in `update_status()` from `self.allocation` (gated
on `ended_datetime IS NULL`), `qty_in`, `qty_out`. The existing three
choices (`AVAILABLE`, `ALLOCATED`, `ZERO_ITEM`) remain sufficient for V1
— exception states (dispensed, damaged, etc.) are queryable via the
boolean flags rather than `status`. Extending `status` to cover
`QUARANTINED`, `DAMAGED`, etc. is deferred to implementation.

### 11.7 Migration plan

Three independent migrations, deployable in any order:

**Migration A — new boolean flags** (trivial, additive):

```python
# Single migration, six AddField operations
migrations.AddField("Stock", "return_requested", models.BooleanField(default=False)),
migrations.AddField("Stock", "quarantined",      models.BooleanField(default=False)),
migrations.AddField("Stock", "damaged",          models.BooleanField(default=False)),
migrations.AddField("Stock", "lost",             models.BooleanField(default=False)),
migrations.AddField("Stock", "expired",          models.BooleanField(default=False)),
migrations.AddField("Stock", "voided",           models.BooleanField(default=False)),
```

No data migration. All existing stock defaults to `False`. On MySQL /
InnoDB, `ADD COLUMN ... DEFAULT FALSE NOT NULL` is an instant metadata
operation — no table rebuild.

**Migration B — Allocation FK refactor** (4-step, in memory doc). Can
run before or after Migration A.

**Migration C — StockTransaction schema expansion** (additive columns,
then indexes and constraints). Covered in the memory doc §"Expanded
StockTransaction schema". Must land before any `apply_transaction` call
writes ledger rows.

No application code changes (signal deletions, `apply_transaction` wiring)
land until Migrations A and C are in. Migration B can trail — the
`apply_transaction` machinery reads `Stock.allocation` only after B
deploys; until then the deprecated OneToOne accessor bridge keeps
existing code working.

---

## 12. Next sketch

- **(c)** Bootstrap migration — synthesise historical `StockTransaction`
  rows from current data so projection equals replay on day one.

---

## 13. Deployment steps — live database

Run these commands in order when deploying with all PRs merged into develop.

`fix_historical_stock_state` must run **before** `bootstrap_stock_transactions`
because it creates `TXN_REPACK_CONSUMED` rows (with a `repack_request` FK) for
repacked bulk stock.  Bootstrap then detects those stocks as already having
transactions and only backfills the missing `TXN_RECEIVED` row.  Running
`fix_historical_stock_state` a **second time** after bootstrap applies the
`repack_consumed_qty_delta` fix (patch `qty_delta=0 → -1` for containers whose
`qty_out=1`); the command is fully idempotent for both runs.

Fixes applied on the **first pass** (before bootstrap):
- in_transit stuck True
- allocation FK not nulled after dispense
- stored_at_location stuck True after dispense
- bootstrapped TXN_RECEIVED qty deltas (no-op before bootstrap, applies after)
- missing TXN_REPACK_CONSUMED rows
- TXN_REPACK_CONSUMED qty_delta=0 (no-op before bootstrap; patches after)
- invalid_state flag for irreconcilable dispensed stocks
- **bulk stock location** — bulk containers (from_stock=None) corrected to central
- **repack child location** — repacked children not yet transferred corrected to central

```bash
# 1. Run all migrations
uv run --dev manage.py migrate

# 2. Fix known pre-refactor Stock column inconsistencies, create
#    TXN_REPACK_CONSUMED rows, and enforce central location for bulk
#    stock and repacked children (must run before bootstrap).
uv run --dev manage.py fix_historical_stock_state

# 3. Back-fill StockTransaction rows for all pre-refactor stock.
#    Idempotent — safe to re-run. Shows a tqdm progress bar.
uv run --dev manage.py bootstrap_stock_transactions

# 4. Second pass — patches TXN_REPACK_CONSUMED qty_delta on containers
#    whose qty_out=1 (set by old repack workflow). All other fixes are
#    idempotent no-ops at this point.
uv run --dev manage.py fix_historical_stock_state

# 5. Verify ledger replay matches Stock cache columns.
#    Expected result: N OK, 0 discrepancies, small number with no transactions.
uv run --dev manage.py check_stock_ledger
```

### After confirming ledger is clean

The `Stock.invalid_state` field (migration 0140) is a temporary marker.
Once the ledger check confirms 0 discrepancies on the live database for
several days, drop it:

```bash
# Generate and run the migration to remove Stock.invalid_state
# (do this in a new PR — feat/pharmacy-drop-invalid-state)
```
