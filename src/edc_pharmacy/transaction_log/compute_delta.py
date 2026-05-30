from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from ..constants import (
    ALLOCATION_END_REASONS,
    TXN_ADJUSTED,
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
    TXN_REVERSAL,
    TXN_STORED,
    TXN_TRANSFER_DISPATCHED,
    TXN_TRANSFER_RECEIVED,
    TXN_VOIDED,
)
from .state_delta import CurrentState, StateDelta


def _check_not_terminal(current_state: CurrentState) -> list[str]:
    """Return failure strings for any active terminal state."""
    fails = []
    if current_state.dispensed:
        fails.append("already dispensed")
    if current_state.destroyed:
        fails.append("already destroyed")
    if current_state.lost:
        fails.append("already lost")
    if current_state.expired:
        fails.append("already expired")
    if current_state.voided:
        fails.append("already voided")
    return fails


def _compute_received(
    current_state: CurrentState, *, confirmed_datetime=None, confirmed_by: str = "", **_
) -> StateDelta:
    if current_state.confirmed:
        return StateDelta(preconditions_failed=("already confirmed",))
    return StateDelta(
        stock_fields={
            "confirmed": True,
            "confirmed_datetime": confirmed_datetime,
            "confirmed_by": confirmed_by,
        },
        confirmation="create",
    )


def _compute_repack_consumed(
    current_state: CurrentState,
    *,
    qty_delta: Decimal,
    unit_qty_delta: Decimal | None = None,
    **_,
) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if unit_qty_delta is not None and unit_qty_delta < 0:
        available = current_state.unit_qty_in - current_state.unit_qty_out
        if abs(unit_qty_delta) > available:
            fail.append(f"insufficient units: need {abs(unit_qty_delta)}, have {available}")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(qty_delta=qty_delta, unit_qty_delta=unit_qty_delta)


def _compute_repack_produced(current_state: CurrentState, **_) -> StateDelta:
    # New stock row produced from repacking; just record the ledger event.
    return StateDelta()


def _compute_allocated(
    current_state: CurrentState, *, registered_subject, stock_request_item, **_
) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.has_allocation:
        # Sticky-pointer policy: Stock.allocation persists past end actions.
        # The only forward path that clears it is REPOOLED. Any other
        # sticky-allocation state must be repooled before re-allocation.
        fail.append("stock still references a prior allocation — repool first")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"subject_identifier": registered_subject.subject_identifier},
        allocation_action="create",
    )


def _compute_allocation_ended(current_state: CurrentState, *, reason: str, **_) -> StateDelta:
    if not current_state.has_allocation:
        return StateDelta(preconditions_failed=("no active allocation",))
    if reason not in ALLOCATION_END_REASONS:
        return StateDelta(preconditions_failed=(f"invalid end reason: {reason!r}",))
    # Sticky-pointer policy: ending the allocation stamps the Allocation row
    # but does NOT clear Stock.allocation or Stock.subject_identifier.
    # Only REPOOLED clears those (see _compute_return_disposition_repooled).
    return StateDelta(
        allocation_action="end",
        allocation_end_reason=reason,
    )


def _compute_transfer_dispatched(
    current_state: CurrentState, *, new_location_id: int, **_
) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.in_transit:
        fail.append("already in transit")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"in_transit": True}
    if current_state.stored_at_location:
        stock_fields["stored_at_location"] = False
    if current_state.confirmed_at_location:
        stock_fields["confirmed_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        storage_bin_item="delete" if current_state.has_storage_bin_item else "unchanged",
        confirmation_at_location_item="delete"
        if current_state.has_confirmation_at_location_item
        else "unchanged",
        new_location_id=new_location_id,
    )


def _compute_transfer_received(
    current_state: CurrentState, *, site_location_id: int, **_
) -> StateDelta:
    fail = []
    if not current_state.in_transit:
        fail.append("not in transit")
    if current_state.confirmed_at_location:
        fail.append("already confirmed at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"in_transit": False, "confirmed_at_location": True},
        confirmation_at_location_item="create",
        new_location_id=site_location_id,
    )


def _compute_stored(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.stored_at_location:
        fail.append("already stored at location")
    if current_state.in_transit:
        fail.append("in transit — cannot store")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"stored_at_location": True},
        storage_bin_item="create",
    )


def _compute_bin_moved(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if not current_state.stored_at_location:
        fail.append("not stored at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    # "replace" = delete existing StorageBinItem then create new one in _apply_delta.
    return StateDelta(storage_bin_item="replace")


def _compute_dispensed(current_state: CurrentState, **_) -> StateDelta:
    fail = []
    if current_state.dispensed:
        fail.append("already dispensed")
    if not current_state.stored_at_location:
        fail.append("not stored at location")
    if not current_state.has_allocation:
        fail.append("no active allocation")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={
            "dispensed": True,
            "stored_at_location": False,
            # subject_identifier and Stock.allocation are intentionally
            # preserved (sticky-pointer policy) — dispense is terminal,
            # the bottle's recipient is a permanent record.
        },
        dispense_item="create",
        storage_bin_item="delete",
        allocation_action="end",
        allocation_end_reason="dispensed",
        qty_delta=Decimal(-1),
        unit_qty_delta=-current_state.container_unit_qty,
    )


def _compute_return_requested(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.return_requested:
        fail.append("return already requested")
    if current_state.in_transit:
        fail.append("in transit")
    if not current_state.stored_at_location:
        fail.append("not stored at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(stock_fields={"return_requested": True})


def _compute_return_dispatched(
    current_state: CurrentState, *, central_location_id: int, **_
) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if not current_state.return_requested:
        fail.append("return not requested")
    if not current_state.stored_at_location:
        fail.append("not stored at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    # Allocation is NOT ended here — stock remains allocated to the subject
    # while in transit and while held at central awaiting disposition.
    # The allocation ends only at final disposition (repooled/quarantined/destroyed).
    return StateDelta(
        stock_fields={
            "return_requested": False,
            "in_transit": True,
            "stored_at_location": False,
            "confirmed_at_location": False,
        },
        storage_bin_item="delete",
        new_location_id=central_location_id,
    )


def _compute_return_received(
    current_state: CurrentState, *, central_location_id: int, **_
) -> StateDelta:
    if not current_state.in_transit:
        return StateDelta(preconditions_failed=("not in transit",))
    return StateDelta(
        stock_fields={"in_transit": False, "confirmed_at_location": False},
        new_location_id=central_location_id,
    )


def _compute_return_disposition_repooled(current_state: CurrentState, **_) -> StateDelta:
    if current_state.in_transit:
        return StateDelta(preconditions_failed=("still in transit",))
    # Repool is the ONE forward transaction that severs the subject link:
    # the bottle re-enters the available pool and may be allocated to
    # a different subject. Clear both the FK (Stock.allocation) and the
    # subject_identifier cache. The Allocation row itself is preserved
    # (with ended_reason="repooled") for the historical audit trail.
    return StateDelta(
        stock_fields={"quarantined": False, "subject_identifier": ""},
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="repooled" if current_state.has_allocation else None,
        clear_allocation=True,
    )


def _compute_return_disposition_quarantined(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.in_transit:
        fail.append("still in transit")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    # Sticky-pointer policy: held in quarantine — Stock.allocation and
    # subject_identifier are preserved. A subsequent REPOOLED would clear them.
    return StateDelta(
        stock_fields={"quarantined": True},
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="quarantined" if current_state.has_allocation else None,
    )


def _compute_return_disposition_destroyed(current_state: CurrentState, **_) -> StateDelta:
    if current_state.destroyed:
        return StateDelta(preconditions_failed=("already destroyed",))
    if current_state.in_transit:
        return StateDelta(preconditions_failed=("still in transit",))
    # Sticky-pointer policy: bottle is destroyed but the link to the
    # subject it had been allocated to is preserved as a permanent record.
    return StateDelta(
        stock_fields={"destroyed": True, "quarantined": False},
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="destroyed" if current_state.has_allocation else None,
    )


def _compute_adjusted(
    current_state: CurrentState, *, unit_qty_delta: Decimal, **_
) -> StateDelta:
    if unit_qty_delta < 0:
        available = current_state.unit_qty_in - current_state.unit_qty_out
        if abs(unit_qty_delta) > available:
            return StateDelta(
                preconditions_failed=(
                    f"adjustment of {unit_qty_delta} exceeds available units "
                    f"({available} remaining)",
                )
            )
    return StateDelta(unit_qty_delta=unit_qty_delta)


def _compute_damaged(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.damaged:
        fail.append("already damaged")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"damaged": True}
    if current_state.stored_at_location:
        stock_fields["stored_at_location"] = False
    remaining_units = current_state.unit_qty_in - current_state.unit_qty_out
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="damaged" if current_state.has_allocation else None,
        storage_bin_item="delete" if current_state.stored_at_location else "unchanged",
        qty_delta=Decimal(-1),
        unit_qty_delta=-remaining_units,
    )


def _compute_lost(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if current_state.damaged:
        fail.append("already damaged — use DAMAGED pathway")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"lost": True}
    if current_state.stored_at_location:
        stock_fields["stored_at_location"] = False
    remaining_units = current_state.unit_qty_in - current_state.unit_qty_out
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="lost" if current_state.has_allocation else None,
        storage_bin_item="delete" if current_state.stored_at_location else "unchanged",
        qty_delta=Decimal(-1),
        unit_qty_delta=-remaining_units,
    )


def _compute_expired(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"expired": True}
    if current_state.stored_at_location:
        stock_fields["stored_at_location"] = False
    remaining_units = current_state.unit_qty_in - current_state.unit_qty_out
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="expired" if current_state.has_allocation else None,
        storage_bin_item="delete" if current_state.stored_at_location else "unchanged",
        qty_delta=Decimal(-1),
        unit_qty_delta=-remaining_units,
    )


def _compute_voided(current_state: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current_state)
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"voided": True}
    if current_state.stored_at_location:
        stock_fields["stored_at_location"] = False
    remaining_units = current_state.unit_qty_in - current_state.unit_qty_out
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current_state.has_allocation else "unchanged",
        allocation_end_reason="voided" if current_state.has_allocation else None,
        storage_bin_item="delete" if current_state.stored_at_location else "unchanged",
        qty_delta=Decimal(-1),
        unit_qty_delta=-remaining_units,
    )


def _compute_reversal(current_state: CurrentState, **_) -> StateDelta:
    raise NotImplementedError("REVERSAL machinery is V2")


_COMPUTERS: dict[str, Callable[..., StateDelta]] = {
    TXN_RECEIVED: _compute_received,
    TXN_REPACK_CONSUMED: _compute_repack_consumed,
    TXN_REPACK_PRODUCED: _compute_repack_produced,
    TXN_ALLOCATED: _compute_allocated,
    TXN_ALLOCATION_ENDED: _compute_allocation_ended,
    TXN_TRANSFER_DISPATCHED: _compute_transfer_dispatched,
    TXN_TRANSFER_RECEIVED: _compute_transfer_received,
    TXN_STORED: _compute_stored,
    TXN_BIN_MOVED: _compute_bin_moved,
    TXN_DISPENSED: _compute_dispensed,
    TXN_RETURN_REQUESTED: _compute_return_requested,
    TXN_RETURN_DISPATCHED: _compute_return_dispatched,
    TXN_RETURN_RECEIVED: _compute_return_received,
    TXN_RETURN_DISPOSITION_REPOOLED: _compute_return_disposition_repooled,
    TXN_RETURN_DISPOSITION_QUARANTINED: _compute_return_disposition_quarantined,
    TXN_RETURN_DISPOSITION_DESTROYED: _compute_return_disposition_destroyed,
    TXN_ADJUSTED: _compute_adjusted,
    TXN_DAMAGED: _compute_damaged,
    TXN_LOST: _compute_lost,
    TXN_EXPIRED: _compute_expired,
    TXN_VOIDED: _compute_voided,
    TXN_REVERSAL: _compute_reversal,
}


def compute_delta(txn_type: str, current_state: CurrentState, **kwargs) -> StateDelta:
    computer = _COMPUTERS.get(txn_type)
    if computer is None:
        raise ValueError(f"Unknown transaction type: {txn_type!r}")
    return computer(current_state, **kwargs)
