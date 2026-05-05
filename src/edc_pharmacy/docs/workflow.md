# edc_pharmacy Stock Workflows

## 1. Forward Workflow: Order → Dispense

| Step | Model(s) | TXN constant | What happens |
|------|----------|--------------|--------------|
| 1. Order | `Order` / `OrderItem` | — | Pharmacist records a purchase order to a supplier |
| 2. Receive | `Receive` / `ReceiveItem` → `Stock` (bulk) | — | Bulk stock records created; labels printed |
| 3. Confirm | `Confirmation` (OneToOne → `Stock`) | `TXN_RECEIVED` | Bulk labels scanned back; `Stock.confirmed = True`. **Required before repack — enforced by guard in `process_repack_request`.** |
| 4. Repack | `RepackRequest` → new child `Stock` (patient bottles) | `TXN_REPACK_CONSUMED` on bulk parent; `TXN_REPACK_PRODUCED` on each child | Confirmed bulk stock decanted into patient bottles; new labels printed for each bottle |
| 5. Confirm | `Confirmation` (OneToOne → child `Stock`) | `TXN_RECEIVED` | Patient-bottle labels scanned back; `Stock.confirmed = True` |
| 6. Stock request | `StockRequest` / `StockRequestItem` | — | Site pharmacist requests stock for upcoming appointments |
| 7. Allocate | `Allocation` → `Stock` | `TXN_ALLOCATED` | Central assigns a specific bottle to a subject |
| 8. Print & affix patient barcode | `LabelConfiguration(requires_allocation=True, name="patient_barcode")` | — | Patient-specific label printed and affixed to bottle. Requires active allocation — enforced by `PrintLabelsView`. |
| 9. Transfer | `StockTransfer` / `StockTransferItem` | `TXN_TRANSFER_DISPATCHED` | Central pharmacist scans allocated bottles into the transfer; manifest printed; boxes shipped to site |
| 10. Confirm at location | `ConfirmationAtLocation` / `ConfirmationAtLocationItem` | `TXN_TRANSFER_RECEIVED` | Site scans codes on arrival |
| 11. Store | `StorageBin` / `StorageBinItem` | `TXN_STORED` | Stock placed in physical bin |
| 12. Dispense | `Dispense` / `DispenseItem` (OneToOne → `Stock`) | `TXN_DISPENSED` | Bottle handed to patient |

### TXN_REPACK_CONSUMED vs TXN_REPACK_PRODUCED

Repack produces two distinct transaction types because it involves two different Stock records:

- **`TXN_REPACK_CONSUMED`** — written once on the **bulk parent** (`from_stock`). Carries a negative `unit_qty_delta` equal to the total units drawn from it across the entire repack run. Reduces the parent's balance without deleting the record.

- **`TXN_REPACK_PRODUCED`** — written once on **each new child** Stock row (patient bottle) as it is created. Records the bottle entering the system with its `container_unit_qty`.

Together they form a balanced ledger entry: the units removed from the parent equal the sum of units added across all children.

### FK chain (forward)

```
Order → OrderItem → ReceiveItem → Stock (bulk)
                                  Stock (bulk) → Confirmation
                                  Stock (bulk) → RepackRequest → Stock (child, per bottle)
                                                                  Stock (child) → Confirmation
StockRequest → StockRequestItem → Allocation → Stock (child)
StockTransfer → StockTransferItem → Stock (child)
ConfirmationAtLocation → ConfirmationAtLocationItem → Stock (child)
StorageBin → StorageBinItem → Stock (child)
Dispense → DispenseItem → Stock (child)
```

### Key Stock boolean flags (forward)

| Flag | Set at step |
|------|-------------|
| `confirmed` | 3 — bulk label scan-back; 5 — patient-bottle label scan-back |
| `in_transit` | 9 — transfer dispatched |
| `confirmed_at_location` | 10 — site scan-back |
| `stored_at_location` | 11 — placed in bin |
| `dispensed` | 12 — handed to patient |

---

## 2. Return Workflow

| Step | Model(s) | TXN constant | What happens |
|------|----------|--------------|--------------|
| 1. Request | `Stock.return_requested = True` | `TXN_RETURN_REQUESTED` | Site pharmacist flags bottles for return |
| 2. Dispatch | `ReturnRequest` / `ReturnItem` created | `TXN_RETURN_DISPATCHED` | Site ships stock back to central; `Stock.in_transit = True` |
| 3. Receive | — | `TXN_RETURN_RECEIVED` | Central scans codes on arrival; `in_transit` cleared |
| 4. Disposition | — | `TXN_RETURN_DISPOSITION_REPOOLED` / `_QUARANTINED` / `_DESTROYED` | Central decides the fate of each bottle |

### Disposition outcomes

| Disposition | Effect on Stock |
|-------------|----------------|
| `REPOOLED` | `Stock.allocation` cleared → `Stock.status = AVAILABLE` → eligible for re-allocation |
| `QUARANTINED` | `Stock.quarantined = True`; allocation pointer preserved; not re-usable |
| `DESTROYED` | `Stock.destroyed = True`; allocation pointer preserved; not re-usable |

---

## 3. Return + Re-allocate Workflow

`Stock.allocation` is a **sticky pointer** — it is only cleared by `TXN_RETURN_DISPOSITION_REPOOLED`. That disposition is the sole gateway back into the supply chain.

```
Dispense
  → [subject returns bottle]
  → Return request        (TXN_RETURN_REQUESTED)
  → Dispatch to central   (TXN_RETURN_DISPATCHED)
  → Receive at central    (TXN_RETURN_RECEIVED)
  → Disposition: REPOOLED (TXN_RETURN_DISPOSITION_REPOOLED)
      → Stock.allocation cleared
      → Stock.status = AVAILABLE
      → Stock enters next StockRequest cycle
          → new Allocation (TXN_ALLOCATED)
          → Transfer → Confirm at location → Store → Dispense
```

Quarantined and destroyed bottles retain their original `Allocation` pointer and never re-enter the supply chain.

---

## 4. Transaction Log

Every state change is recorded in `StockTransaction` (append-only ledger).

| Field | Purpose |
|-------|---------|
| `transaction_type` | `TXN_*` constant identifying the step |
| `transaction_datetime` | When it occurred |
| `actor` | User who triggered it |
| `from_location` / `to_location` | Location movement |
| `from_allocation` / `to_allocation` | Allocation movement |
| `from_bin` / `to_bin` | Storage bin movement |
| `qty_delta` / `unit_qty_delta` | Signed quantity change (negative for consumption) |
| `state_after` | JSON snapshot of Stock state post-transaction |
| `reverses` | Self-FK — links a reversal to the original transaction |

Source FKs present on each row (whichever applies): `receive_item`, `repack_request`, `stock_transfer_item`, `dispense_item`, `return_item`.

---

## 5. URL Map by Workflow Step

```
ORDER
  order_home_url                    OrderHomeView
  order_add_url                     OrderEditView (create)
  order_url                         OrderView (read)
  order_edit_url                    OrderEditView (update)
  order_item_add_url                OrderItemEditView
  order_item_edit_url               OrderItemEditView
  print_order_url                   print_order_view

RECEIVE
  receive_home_url                  ReceiveHomeView
  receive_order_url                 ReceiveOrderView
  receive_order_edit_url            ReceiveOrderEditView
  receive_order_item_url            ReceiveOrderItemView (add)
  receive_item_edit_url             ReceiveOrderItemView (edit)
  receive_edit_url                  ReceiveEditView
  receive_stock_list_url            ReceiveStockListView
  receive_lot_add_url               ReceiveLotAddView
  receive_supplier_add_url          ReceiveSupplierAddView
  receive_supplier_edit_url         ReceiveSupplierEditView

CONFIRM (post-receive — required before repack)
  Triggered from ReceiveOrderView via [Print labels] / [Confirm labelled stock] buttons.
  No admin changelist required.
  print_labels_url                  PrintLabelsView
  confirm_stock_from_queryset_url   ConfirmStockFromQuerySetView

REPACK
  repack_home_url                   RepackHomeView
  repack_add_url                    RepackEditView (create)
  repack_url                        RepackView (execute)
  repack_edit_url                   RepackEditView (update)

CONFIRM (post-repack)
  Triggered from RepackView via [Print labels] / [Confirm labelled stock] buttons.
  No admin changelist required.
  print_labels_url                  PrintLabelsView
  confirm_stock_from_queryset_url   ConfirmStockFromQuerySetView

STOCK REQUEST
  stock_request_home_url            StockRequestHomeView
  stock_request_add_url             StockRequestEditView (create)
  stock_request_url                 StockRequestView (read)
  stock_request_edit_url            StockRequestEditView (update)
  review_stock_request_url          PrepareAndReviewStockRequestView

ALLOCATE
  allocate_url                      AllocateToSubjectView

PRINT PATIENT BARCODE (post-allocation, pre-transfer)
  print_labels_url                  PrintLabelsView (label_configuration=patient_barcode)
  (triggered from StockRequestItem admin via print_labels_from_stock_request_item
   or print_labels_from_stock_request_by_code)

TRANSFER
  stock_transfer_home_url           StockTransferHomeView
  stock_transfer_add_url            StockTransferEditView (create)
  stock_transfer_edit_url           StockTransferEditView (update)
  transfer_stock_url                TransferStockView (dispatch)

CONFIRM AT LOCATION
  confirm_at_location_url           ConfirmaAtLocationView
  print_stock_transfer_manifest     print_stock_transfer_manifest_view

STORE
  add_to_storage_bin_url            AddToStorageBinView
  move_to_storage_bin_url           MoveToStorageBinView

DISPENSE
  dispense_url                      DispenseView

RETURN
  return_request_url                ReturnRequestView (request & dispatch)
  return_central_url                ReturnCentralView
  return_receive_url                ReturnReceiveView
  return_disposition_url            ReturnDispositionView
  print_return_manifest_view        print_return_manifest_view
```
