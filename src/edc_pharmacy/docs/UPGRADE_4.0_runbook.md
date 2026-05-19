# edc-pharmacy 4.0.0 — upgrade verification runbook

A practical runbook for verifying a 4.0.0 upgrade against a staging copy of production data **before** running it for real on production.

Companion to `UPGRADE_4.0.md`, which documents *what* changed. This file is *how to confirm the change is safe in your data*.

The expected output of this runbook is a short go/no-go report (template at the bottom).

---

## 0. Prerequisites

- Most recent production database backup, restored to a **staging** database.
- A staging deployment running the 4.0.0 code, pointed at that database.
- Network/auth set up so you can run `manage.py` commands and `manage.py shell` against the staging DB.
- Substitute `<your.settings>` below with your settings module (e.g. `meta_edc.settings.staging`).

---

## 1. Dry-runs

Before mutating anything, see what's coming.

```bash
uv run --dev manage.py migrate --plan --settings=<your.settings>
```

The dry-runs for the management commands cannot be run yet — they require the 4.0.0 schema (`StockTransaction` ledger fields, `Allocation.stock` back-pointer, etc.) which only lands after `migrate`. See § 3 for those.

Record:
- [ ] Migrations listed (expect `0139`–`0157`)

---

## 2. Run migrations only

Migrations are run on their own first, so the next step (the pre-fix snapshot) can use the 4.0.0 ORM against the new schema.

```bash
time uv run --dev manage.py migrate --settings=<your.settings>
```

Capture one number from the migration output:
- [ ] `0157_backfill_allocation_stock_backpointer` — the tqdm progress bar reports how many `Allocation` rows had their `stock` back-pointer backfilled. This is the *only* place that count exists; record it from the log. (Post-snapshot will show `Allocation.stock_id IS NULL` count = 0 — the migration already did its work.)

At this point: the schema is 4.0.0 but no cached `Stock` columns have been touched by `fix_historical_stock_state` or `bootstrap_stock_transactions` yet.

---

## 3. Pre-fix invariant snapshot and command dry-runs

The pre-snapshot is captured here — **after** `migrate` but **before** any data-transformation command. The cached Stock columns are still whatever they were on 3.1.5; only the schema has moved.

### 3a. Snapshot

```python
# scripts/pre_upgrade_invariants.py
# Run via: manage.py shell --settings=<your.settings> < scripts/pre_upgrade_invariants.py
import json
from decimal import Decimal
from django.db.models import Sum

from edc_pharmacy.models import (
    Allocation,
    DispenseItem,
    Stock,
    StockTransferItem,
    StorageBinItem,
    ConfirmationAtLocationItem,
)


def _as_str_dec(x):
    return str(x or Decimal("0"))


snapshot = {
    # Totals — must NOT change across upgrade.
    "stocks_total": Stock.objects.count(),
    "dispense_items": DispenseItem.objects.count(),
    "stock_transfer_items": StockTransferItem.objects.count(),
    "storage_bin_items": StorageBinItem.objects.count(),
    "confirmation_at_location_items": ConfirmationAtLocationItem.objects.count(),

    # Stock cache columns — `fix_historical_stock_state` may correct some of
    # these (stuck `in_transit`, dispense not nulling `allocation`, etc.).
    # Capture the deltas; cross-reference against the per-rule counts the
    # command prints to confirm each delta is accounted for.
    "stocks_confirmed": Stock.objects.filter(confirmed=True).count(),
    "stocks_confirmed_at_location": Stock.objects.filter(confirmed_at_location=True).count(),
    "stocks_in_transit": Stock.objects.filter(in_transit=True).count(),
    "stocks_stored_at_location": Stock.objects.filter(stored_at_location=True).count(),
    "stocks_dispensed": Stock.objects.filter(dispensed=True).count(),
    "stocks_allocated": Stock.objects.filter(allocation__isnull=False).count(),

    # Aggregate qty — must NOT change.
    "qty_in_total": _as_str_dec(Stock.objects.aggregate(s=Sum("qty_in"))["s"]),
    "qty_out_total": _as_str_dec(Stock.objects.aggregate(s=Sum("qty_out"))["s"]),
    "unit_qty_in_total": _as_str_dec(Stock.objects.aggregate(s=Sum("unit_qty_in"))["s"]),
    "unit_qty_out_total": _as_str_dec(Stock.objects.aggregate(s=Sum("unit_qty_out"))["s"]),

    # Allocation counts. In 3.1.5 Allocation was a OneToOneField and the
    # row was deleted when stock was dispensed. In 4.0.0 it's a sticky
    # ForeignKey and rows may accumulate (ended_datetime IS NOT NULL). The
    # pre-snapshot number is therefore a LOWER bound on the post-snapshot.
    "allocations": Allocation.objects.count(),

    # Subjects with at least one allocated stock — should not change.
    "subjects_with_allocations": (
        Allocation.objects.values("subject_identifier").distinct().count()
    ),
}

with open("upgrade_invariants_pre.json", "w") as f:
    json.dump(snapshot, f, indent=2, sort_keys=True)
print(json.dumps(snapshot, indent=2, sort_keys=True))
```

```bash
mkdir -p scripts
# Save the script above as scripts/pre_upgrade_invariants.py, then:
uv run --dev manage.py shell --settings=<your.settings> < scripts/pre_upgrade_invariants.py
```

Outputs `upgrade_invariants_pre.json` in the project working directory.

> **Note on `allocations_with_null_stock`.** This metric is intentionally
> omitted from the snapshot. Migration 0157 (run during § 2) backfills
> the back-pointer before any ORM-level snapshot can see it. Read the
> count from the `0157_backfill_allocation_stock_backpointer` tqdm output
> in the migrate log instead.

### 3b. Command dry-runs

Now that the schema is 4.0.0, the dry-runs work.

```bash
uv run --dev manage.py fix_historical_stock_state --dry-run --settings=<your.settings>
uv run --dev manage.py bootstrap_stock_transactions --dry-run --settings=<your.settings>
```

Record:
- [ ] `fix_historical_stock_state` per-rule counts (first-pass dry-run):
  - [ ] `[in_transit]` count
  - [ ] `[allocation]` count
  - [ ] `[stored_at_location]` count
  - [ ] `[qty_delta]` count
  - [ ] `[repack_consumed]` count
  - [ ] `[repack_consumed_qty_delta]` count
  - [ ] `[invalid]` count
  - [ ] `[bulk_location]` count
  - [ ] `[repack_child_location]` count
  - [ ] `[bootstrapped_txn_locations]` count (expected ~0 on first pass)
  - [ ] `[allocation_backpointer]` count (expected 0 — migration 0157 already ran)
- [ ] `bootstrap_stock_transactions` "would create N transactions" count

Surprising counts (all zeros where you expected fixes, or wildly large) are flags to investigate before running for real.

---

## 4. Run the data-transformation sequence

Time each step. On any non-zero exit, **stop and investigate** — don't run the next step.

```bash
time uv run --dev manage.py fix_historical_stock_state --settings=<your.settings> && \
time uv run --dev manage.py bootstrap_stock_transactions --settings=<your.settings> && \
time uv run --dev manage.py fix_historical_stock_state --settings=<your.settings> && \
time uv run --dev manage.py check_stock_ledger --settings=<your.settings>
```

Record wall-clock times — they bound your production maintenance window.

`check_stock_ledger` exit 0 is the **gate**. On non-zero exit, run with `--stock-code <code>` for each reported code to debug.

---

## 5. Post-upgrade invariant snapshot

```python
# scripts/post_upgrade_invariants.py
# Same script as pre, but writes to a different file. Just copy and
# change the output filename, or refactor into one script with a CLI arg.
import json
from decimal import Decimal
from django.db.models import Sum

from edc_pharmacy.models import (
    Allocation,
    DispenseItem,
    Stock,
    StockTransaction,
    StockTransferItem,
    StorageBinItem,
    ConfirmationAtLocationItem,
)


def _as_str_dec(x):
    return str(x or Decimal("0"))


snapshot = {
    # Same fields as pre.
    "stocks_total": Stock.objects.count(),
    "dispense_items": DispenseItem.objects.count(),
    "stock_transfer_items": StockTransferItem.objects.count(),
    "storage_bin_items": StorageBinItem.objects.count(),
    "confirmation_at_location_items": ConfirmationAtLocationItem.objects.count(),
    "stocks_confirmed": Stock.objects.filter(confirmed=True).count(),
    "stocks_confirmed_at_location": Stock.objects.filter(confirmed_at_location=True).count(),
    "stocks_in_transit": Stock.objects.filter(in_transit=True).count(),
    "stocks_stored_at_location": Stock.objects.filter(stored_at_location=True).count(),
    "stocks_dispensed": Stock.objects.filter(dispensed=True).count(),
    "stocks_allocated": Stock.objects.filter(allocation__isnull=False).count(),
    "qty_in_total": _as_str_dec(Stock.objects.aggregate(s=Sum("qty_in"))["s"]),
    "qty_out_total": _as_str_dec(Stock.objects.aggregate(s=Sum("qty_out"))["s"]),
    "unit_qty_in_total": _as_str_dec(Stock.objects.aggregate(s=Sum("unit_qty_in"))["s"]),
    "unit_qty_out_total": _as_str_dec(Stock.objects.aggregate(s=Sum("unit_qty_out"))["s"]),
    "allocations": Allocation.objects.count(),
    "subjects_with_allocations": (
        Allocation.objects.values("subject_identifier").distinct().count()
    ),
    # Post-upgrade additions: ledger health.
    "stock_transactions_total": StockTransaction.objects.count(),
    "stocks_with_ledger": (
        Stock.objects.filter(transactions__isnull=False).distinct().count()
    ),
    "stocks_without_ledger": (
        Stock.objects.filter(transactions__isnull=True).count()
    ),
    "allocations_active": Allocation.objects.filter(ended_datetime__isnull=True).count(),
    "allocations_ended": Allocation.objects.filter(ended_datetime__isnull=False).count(),
}

with open("upgrade_invariants_post.json", "w") as f:
    json.dump(snapshot, f, indent=2, sort_keys=True)
print(json.dumps(snapshot, indent=2, sort_keys=True))
```

```bash
uv run --dev manage.py shell --settings=<your.settings> < scripts/post_upgrade_invariants.py
```

---

## 6. Diff the snapshots

```python
# scripts/diff_upgrade_invariants.py
# Run: python scripts/diff_upgrade_invariants.py
import json

with open("upgrade_invariants_pre.json") as f:
    pre = json.load(f)
with open("upgrade_invariants_post.json") as f:
    post = json.load(f)

MUST_NOT_CHANGE = (
    "stocks_total",
    "dispense_items",
    "stock_transfer_items",
    "storage_bin_items",
    "confirmation_at_location_items",
    "qty_in_total",
    "qty_out_total",
    "unit_qty_in_total",
    "unit_qty_out_total",
    "subjects_with_allocations",
)
EXPECTED_TO_GROW = ("allocations",)  # sticky-pointer accumulation
EXPECTED_TO_APPEAR = ("stock_transactions_total",)  # was ~0 pre-bootstrap

print("=== MUST_NOT_CHANGE ===")
for k in MUST_NOT_CHANGE:
    pre_v, post_v = pre.get(k), post.get(k)
    marker = "OK" if pre_v == post_v else "*** DRIFT ***"
    print(f"  {marker:14s} {k}: pre={pre_v} post={post_v}")

print("\n=== EXPECTED_TO_GROW ===")
for k in EXPECTED_TO_GROW:
    pre_v, post_v = pre.get(k), post.get(k)
    marker = "OK" if post_v >= pre_v else "*** SHRANK ***"
    print(f"  {marker:16s} {k}: pre={pre_v} post={post_v}")

print("\n=== EXPECTED_TO_APPEAR ===")
for k in EXPECTED_TO_APPEAR:
    post_v = post.get(k)
    marker = "OK" if post_v > 0 else "*** STILL ZERO ***"
    print(f"  {marker:18s} {k}: post={post_v}")

print("\n=== Cached-column counts (compare visually) ===")
for k in (
    "stocks_confirmed",
    "stocks_confirmed_at_location",
    "stocks_in_transit",
    "stocks_stored_at_location",
    "stocks_dispensed",
    "stocks_allocated",
):
    print(f"  {k}: pre={pre.get(k)} post={post.get(k)}")
```

Eyeball the cached-column counts. They *may* change slightly if `fix_historical_stock_state` corrected stuck-true flags (e.g. `in_transit`). Cross-reference any change against the `fix_historical_stock_state` output from step 4 — if the rule fired, the delta is expected and quantifiable.

---

## 7. Spot-check sample stocks

For each of these lifecycle shapes, pick a couple of stock codes and walk the ledger in `manage.py shell`. Use codes you recognize.

```python
from edc_pharmacy.models import Stock
def walk(code):
    s = Stock.objects.get(code=code)
    print(f"\n=== {code} ===")
    print(f"  state: confirmed={s.confirmed} in_transit={s.in_transit} "
          f"stored={s.stored_at_location} dispensed={s.dispensed} "
          f"location={s.location} allocation={s.allocation_id}")
    for t in s.transactions.order_by("transaction_datetime"):
        print(f"  {t.transaction_datetime:%Y-%m-%d %H:%M}  {t.transaction_type:24s} "
              f"qty_delta={t.qty_delta} unit_qty_delta={t.unit_qty_delta}")
```

Shapes worth picking on purpose:
- [ ] A stock currently at central, confirmed, never dispensed — expect only `TXN_RECEIVED`
- [ ] A stock dispensed at a site — expect RECEIVED → ALLOCATED → TRANSFER_DISPATCHED → TRANSFER_RECEIVED → STORED → DISPENSED
- [ ] A stock transferred more than once (central → site → central → site if your study has this)
- [ ] A child of a repack (`stock.repack_request_id IS NOT NULL`) — expect TXN_REPACK_PRODUCED
- [ ] A bulk parent of a repack — expect TXN_REPACK_CONSUMED on the parent
- [ ] A stock marked `invalid_state=True` (the three known cases UGNXMR, 4992XB, 94UQKG, or however many your DB has)
- [ ] A stock with `damaged`/`expired`/`lost`/`voided` set — expect a corresponding `TXN_*` adjustment row

---

## 8. UI smoke test on staging

Each row = one workflow exercise. Tick when you've completed it on staging and verified the listed expectations.

| # | Flow | Action | Expect |
|---|---|---|---|
| [ ] | Receive | Confirm a labelled stock via "Confirm labelled stock" | `TXN_RECEIVED` row written, `Stock.confirmed=True`, success message |
| [ ] | Receive — already confirmed | Re-scan a code that was just confirmed | Bucketed as `already_confirmed`, NOT counted as invalid |
| [ ] | Receive — invalid | Scan a foreign barcode | Bucketed as `invalid` |
| [ ] | Allocate | Allocate via AllocateToSubjectView | `TXN_ALLOCATED`, `Allocation.stock` populated (not NULL) |
| [ ] | Transfer dispatch | Dispatch a transfer | `TXN_TRANSFER_DISPATCHED`, `in_transit=True` |
| [ ] | Transfer receive | Scan at receiving site | `TXN_TRANSFER_RECEIVED`, `confirmed_at_location=True`, `in_transit=False` |
| [ ] | Store in bin | Add to storage bin | `TXN_STORED`, `stored_at_location=True`, `StorageBinItem` created |
| [ ] | Store — already stored | Re-scan into the same bin | Bucketed as `already_stored` (NEW: separate from `invalid`) |
| [ ] | Move bin | Move from bin A to bin B | `TXN_BIN_MOVED`, old `StorageBinItem` deleted, new one in bin B |
| [ ] | Dispense | Scan to a subject | `TXN_DISPENSED`, ledger qty_delta=-1 |
| [ ] | Dispense — wrong subject | Scan a stock allocated to a different subject | Whole batch aborts (NEW safety policy) |
| [ ] | Dispense — already dispensed | Re-scan an already-dispensed code | Bucketed as `already_dispensed` |
| [ ] | Adjust — lost | Mark a stock as lost via the stock-adjustment view | `TXN_LOST`, `Stock.lost=True` |
| [ ] | Adjust — qty | Apply a quantity adjustment | `TXN_ADJUSTED`, ledger qty/unit_qty deltas right |
| [ ] | Return — request | Mark stock for return | `TXN_RETURN_REQUESTED`, `Stock.return_requested=True` |
| [ ] | Return — dispatch | Site dispatches return | `TXN_RETURN_DISPATCHED`, `in_transit=True`, `ReturnItem` created |
| [ ] | Return — receive | Central confirms receipt | `TXN_RETURN_RECEIVED` |
| [ ] | Return — repool | Disposition as repool | `TXN_RETURN_DISPOSITION_REPOOLED`, `Stock.allocation` cleared, ready for re-allocate |
| [ ] | Return — quarantine | Disposition as quarantine | `TXN_RETURN_DISPOSITION_QUARANTINED`, `Stock.quarantined=True` |
| [ ] | Return — destroy | Disposition as destroy | `TXN_RETURN_DISPOSITION_DESTROYED`, `Stock.destroyed=True` |
| [ ] | Stock-take | Run a stock take on a bin with a mix of expected and missing codes | StockTake/StockTakeItem rows; results page renders matched/missing/unexpected counts |
| [ ] | Guard redirects (NEW fix) | POST add-to-bin with duplicate codes in form | Redirect actually fires (was a silent error in 3.1.x) |
| [ ] | Ledger viewer | Open `LedgerView` for one of your spot-check stocks | Reads the full ledger you walked in step 7 |

---

## 9. Performance findings

Capture wall-clock times from steps 2 and 4 here. These define your production maintenance window.

| Step | Time | Notes |
|---|---|---|
| `migrate` | _____ | |
| `fix_historical_stock_state` (1st) | _____ | |
| `bootstrap_stock_transactions` | _____ | Single longest step. If > deploy window, consider `--stock-code` slicing. |
| `fix_historical_stock_state` (2nd) | _____ | |
| `check_stock_ledger` | _____ | |
| Total | _____ | |

---

## 10. Go/no-go report template

Copy and fill before production deploy.

```
edc-pharmacy 4.0.0 staging verification — <DATE>
=================================================

DB snapshot:                <prod backup tag/date>
Staging environment:        <hostname / branch>
Staging upgrade run by:     <name>

1. Migration plan reviewed (dry-run):          [ ] Y / [ ] N
2. `migrate` ran cleanly:                      [ ] Y / [ ] N
   - Migration 0157 backfilled N allocations:  _____
3. Pre-fix invariants captured:                [ ] Y / [ ] N
   - Command dry-runs reviewed:                [ ] Y / [ ] N
4. Data-transformation sequence completed:     [ ] Y / [ ] N
   - check_stock_ledger exit code:             _____
5. Post-upgrade invariants captured:           [ ] Y / [ ] N
6. Invariant diff:
   - MUST_NOT_CHANGE rows drift:               [ ] none / [ ] see notes
   - stock_transactions_total post:            _____
7. Spot-check sample (>= 5 lifecycle shapes):  [ ] Y / [ ] N
8. UI smoke test rows passed:                  _____ / _____
9. Performance acceptable for prod window:     [ ] Y / [ ] N

Anomalies found / resolved:
  - …

Outstanding concerns (must clear before prod):
  - …

GO / NO-GO:        [ ] GO    [ ] NO-GO
Signed:            ________________________
Date:              ____ - ____ - ________
```

---

## See also

- `UPGRADE_4.0.md` — what changed in 4.0.0 and why
- `DESIGN_transaction_log.md` — architecture rationale
- `workflow.md` — pharmacy operational flows
