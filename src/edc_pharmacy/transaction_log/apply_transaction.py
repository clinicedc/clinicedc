from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

from ..exceptions import InvalidTransitionError
from .compute_delta import compute_delta
from .state_delta import CurrentState, StateDelta
from ._sentinel import apply_delta_context

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from ..models.stock.stock import Stock
    from ..models.stock.stock_transaction import StockTransaction


def _snapshot(stock: Stock) -> CurrentState:
    from ..models.stock.confirmation_at_location_item import ConfirmationAtLocationItem
    from ..models.stock.storage_bin_item import StorageBinItem

    allocation = getattr(stock, "allocation", None)
    has_active_allocation = allocation is not None
    active_allocation_subject = (
        allocation.registered_subject.subject_identifier if has_active_allocation else ""
    )
    try:
        stock.storagebinitem  # noqa: B018
        has_storage_bin_item = True
    except StorageBinItem.DoesNotExist:
        has_storage_bin_item = False
    try:
        stock.confirmationatlocationitem  # noqa: B018
        has_confirmation_at_location_item = True
    except ConfirmationAtLocationItem.DoesNotExist:
        has_confirmation_at_location_item = False
    return CurrentState(
        stock_id=stock.pk,
        location_id=stock.location_id,
        confirmed=stock.confirmed,
        confirmed_at_location=stock.confirmed_at_location,
        stored_at_location=stock.stored_at_location,
        dispensed=stock.dispensed,
        destroyed=stock.destroyed,
        in_transit=stock.in_transit,
        damaged=stock.damaged,
        lost=stock.lost,
        expired=stock.expired,
        voided=stock.voided,
        return_requested=stock.return_requested,
        quarantined=stock.quarantined,
        qty_in=stock.qty_in or Decimal("0"),
        qty_out=stock.qty_out or Decimal("0"),
        unit_qty_in=stock.unit_qty_in or Decimal("0"),
        unit_qty_out=stock.unit_qty_out or Decimal("0"),
        container_unit_qty=stock.container_unit_qty or Decimal("0"),
        has_active_allocation=has_active_allocation,
        active_allocation_subject=active_allocation_subject,
        has_storage_bin_item=has_storage_bin_item,
        has_confirmation_at_location_item=has_confirmation_at_location_item,
    )


def _apply_delta(stock: Stock, delta: StateDelta, **kwargs) -> dict:
    from ..models.stock.allocation import Allocation
    from ..models.stock.confirmation import Confirmation
    from ..models.stock.confirmation_at_location_item import ConfirmationAtLocationItem
    from ..models.stock.dispense_item import DispenseItem
    from ..models.stock.storage_bin_item import StorageBinItem

    update_fields: list[str] = []
    created_objects: dict = {}

    with apply_delta_context():
        # Apply scalar Stock field updates.
        for field_name, value in delta.stock_fields.items():
            setattr(stock, field_name, value)
            update_fields.append(field_name)

        # Apply location change.
        if delta.new_location_id is not None:
            stock.location_id = delta.new_location_id
            update_fields.append("location")

        # Apply signed qty deltas.
        if delta.qty_delta is not None:
            if delta.qty_delta < 0:
                stock.qty_out = stock.qty_out + abs(delta.qty_delta)
                update_fields.append("qty_out")
            else:
                stock.qty_in = stock.qty_in + delta.qty_delta
                update_fields.append("qty_in")

        if delta.unit_qty_delta is not None:
            if delta.unit_qty_delta < 0:
                stock.unit_qty_out = stock.unit_qty_out + abs(delta.unit_qty_delta)
                update_fields.append("unit_qty_out")
            else:
                stock.unit_qty_in = stock.unit_qty_in + delta.unit_qty_delta
                update_fields.append("unit_qty_in")

        # Allocation lifecycle.
        if delta.allocation_action == "create":
            # TODO(allocation-refactor): after Migration B, create an Allocation
            # with started_datetime and set stock.current_allocation.
            # Pre-B: create Allocation and set stock.allocation (OneToOne).
            allocation = kwargs.get("allocation") or Allocation.objects.create(
                registered_subject=kwargs["registered_subject"],
                stock_request_item=kwargs["stock_request_item"],
                allocated_by=kwargs.get("allocated_by", ""),
                code=stock.code,
            )
            stock.allocation = allocation
            update_fields.append("allocation")
            created_objects["to_allocation"] = allocation

        elif delta.allocation_action == "end":
            # TODO(allocation-refactor): after Migration B, set ended_datetime
            # and ended_reason on the active Allocation record instead of nulling it.
            # Pre-B: null the OneToOne FK (history is lost until B is deployed).
            created_objects["from_allocation"] = stock.allocation
            stock.allocation = None
            update_fields.append("allocation")

        # Save all Stock changes in one write.
        if update_fields:
            update_fields.append("status")  # update_status() is called in save()
            stock.save(update_fields=list(set(update_fields)))

    # Child row lifecycle (outside apply_delta_context — these models are not guarded).

    if delta.storage_bin_item in ("delete", "replace"):
        StorageBinItem.objects.filter(stock=stock).delete()

    if delta.confirmation_at_location_item == "delete":
        ConfirmationAtLocationItem.objects.filter(stock=stock).delete()

    if delta.confirmation == "create":
        Confirmation.objects.create(
            stock=stock,
            confirmed_datetime=kwargs.get("confirmed_datetime"),
            confirmed_by=kwargs.get("confirmed_by", ""),
        )

    if delta.confirmation_at_location_item == "create":
        ConfirmationAtLocationItem.objects.create(
            stock=stock,
            confirm_at_location=kwargs["confirm_at_location"],
            stock_transfer_item=kwargs["stock_transfer_item"],
            confirmed_datetime=kwargs.get("confirmed_datetime"),
            confirmed_by=kwargs.get("confirmed_by", ""),
        )

    if delta.storage_bin_item in ("create", "replace"):
        StorageBinItem.objects.create(
            stock=stock,
            storage_bin=kwargs["storage_bin"],
        )

    if delta.dispense_item == "create":
        dispense_item = DispenseItem.objects.create(
            stock=stock,
            dispense=kwargs["dispense"],
        )
        created_objects["dispense_item"] = dispense_item

    return created_objects


def _write_ledger_row(
    stock: Stock,
    txn_type: str,
    delta: StateDelta,
    actor: AbstractUser,
    *,
    reason: str = "",
    **kwargs,
) -> StockTransaction:
    from ..models.stock.stock_transaction import StockTransaction

    state_after = {
        "confirmed": stock.confirmed,
        "confirmed_at_location": stock.confirmed_at_location,
        "stored_at_location": stock.stored_at_location,
        "dispensed": stock.dispensed,
        "destroyed": stock.destroyed,
        "in_transit": stock.in_transit,
        "damaged": stock.damaged,
        "lost": stock.lost,
        "expired": stock.expired,
        "voided": stock.voided,
        "return_requested": stock.return_requested,
        "quarantined": stock.quarantined,
        "location_id": stock.location_id,
        "qty_in": str(stock.qty_in),
        "qty_out": str(stock.qty_out),
        "unit_qty_in": str(stock.unit_qty_in),
        "unit_qty_out": str(stock.unit_qty_out),
    }

    return StockTransaction.objects.create(
        stock=stock,
        transaction_type=txn_type,
        actor=actor,
        reason=reason,
        qty_delta=delta.qty_delta or Decimal("0"),
        unit_qty_delta=delta.unit_qty_delta or Decimal("0"),
        from_location_id=kwargs.get("_from_location_id"),
        to_location_id=stock.location_id,
        from_allocation=kwargs.get("from_allocation"),
        to_allocation=kwargs.get("to_allocation") or getattr(stock, "allocation", None),
        receive_item=kwargs.get("receive_item"),
        repack_request=kwargs.get("repack_request"),
        stock_transfer_item=kwargs.get("stock_transfer_item"),
        dispense_item=kwargs.get("dispense_item"),
        stock_adjustment=kwargs.get("stock_adjustment"),
        return_item=kwargs.get("return_item"),
        state_after=state_after,
    )


def apply_transaction(
    stock: Stock,
    txn_type: str,
    actor: AbstractUser,
    *,
    reason: str = "",
    **kwargs,
) -> StockTransaction:
    from_location_id = stock.location_id
    current = _snapshot(stock)
    delta = compute_delta(txn_type, current, **kwargs)

    if delta.preconditions_failed:
        raise InvalidTransitionError(
            f"{txn_type} refused on stock={stock.code}: "
            f"{'; '.join(delta.preconditions_failed)}"
        )

    with transaction.atomic():
        created = _apply_delta(stock, delta, **kwargs)
        txn = _write_ledger_row(
            stock,
            txn_type,
            delta,
            actor,
            reason=reason,
            _from_location_id=from_location_id,
            **{**kwargs, **created},
        )

    return txn
