from __future__ import annotations

from decimal import Decimal
from typing import Callable

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


def _check_not_terminal(current: CurrentState) -> list[str]:
    """Return failure strings for any active terminal state."""
    fails = []
    if current.dispensed:
        fails.append("already dispensed")
    if current.destroyed:
        fails.append("already destroyed")
    if current.lost:
        fails.append("already lost")
    if current.expired:
        fails.append("already expired")
    if current.voided:
        fails.append("already voided")
    return fails


def _compute_received(current: CurrentState, *, confirmed_datetime=None, confirmed_by: str = "", **_) -> StateDelta:
    if current.confirmed:
        return StateDelta(preconditions_failed=("already confirmed",))
    return StateDelta(
        stock_fields={
            "confirmed": True,
            "confirmed_datetime": confirmed_datetime,
            "confirmed_by": confirmed_by,
        },
        confirmation="create",
    )


def _compute_repack_consumed(current: CurrentState, *, qty_delta: Decimal, unit_qty_delta: Decimal | None = None, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if unit_qty_delta is not None and unit_qty_delta < 0:
        available = current.unit_qty_in - current.unit_qty_out
        if abs(unit_qty_delta) > available:
            fail.append(f"insufficient units: need {abs(unit_qty_delta)}, have {available}")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(qty_delta=qty_delta, unit_qty_delta=unit_qty_delta)


def _compute_repack_produced(current: CurrentState, **_) -> StateDelta:
    # New stock row produced from repacking; just record the ledger event.
    return StateDelta()


def _compute_allocated(current: CurrentState, *, registered_subject, stock_request_item, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.has_active_allocation:
        fail.append("already allocated — end current allocation first")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"subject_identifier": registered_subject.subject_identifier},
        allocation_action="create",
    )


def _compute_allocation_ended(current: CurrentState, *, reason: str, **_) -> StateDelta:
    if not current.has_active_allocation:
        return StateDelta(preconditions_failed=("no active allocation",))
    if reason not in ALLOCATION_END_REASONS:
        return StateDelta(preconditions_failed=(f"invalid end reason: {reason!r}",))
    stock_fields = {}
    if reason != "dispensed":
        # All non-dispense endings sever the subject relationship.
        # For dispensed, subject_identifier is intentionally preserved —
        # the bottle's recipient is permanent record.
        stock_fields["subject_identifier"] = ""
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end",
        allocation_end_reason=reason,
    )


def _compute_transfer_dispatched(current: CurrentState, *, new_location_id: int, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.in_transit:
        fail.append("already in transit")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"in_transit": True}
    if current.stored_at_location:
        stock_fields["stored_at_location"] = False
    if current.confirmed_at_location:
        stock_fields["confirmed_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        storage_bin_item="delete" if current.has_storage_bin_item else "unchanged",
        confirmation_at_location_item="delete" if current.has_confirmation_at_location_item else "unchanged",
        new_location_id=new_location_id,
    )


def _compute_transfer_received(current: CurrentState, *, site_location_id: int, **_) -> StateDelta:
    fail = []
    if not current.in_transit:
        fail.append("not in transit")
    if current.confirmed_at_location:
        fail.append("already confirmed at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"in_transit": False, "confirmed_at_location": True},
        confirmation_at_location_item="create",
        new_location_id=site_location_id,
    )


def _compute_stored(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.stored_at_location:
        fail.append("already stored at location")
    if current.in_transit:
        fail.append("in transit — cannot store")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(
        stock_fields={"stored_at_location": True},
        storage_bin_item="create",
    )


def _compute_bin_moved(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if not current.stored_at_location:
        fail.append("not stored at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    # "replace" = delete existing StorageBinItem then create new one in _apply_delta.
    return StateDelta(storage_bin_item="replace")


def _compute_dispensed(current: CurrentState, **_) -> StateDelta:
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
            # subject_identifier intentionally NOT cleared: dispense is terminal —
            # the bottle's recipient is permanent record.
        },
        dispense_item="create",
        storage_bin_item="delete",
        allocation_action="end",
        allocation_end_reason="dispensed",
        qty_delta=Decimal("-1"),
        unit_qty_delta=-current.container_unit_qty,
    )


def _compute_return_requested(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.return_requested:
        fail.append("return already requested")
    if current.in_transit:
        fail.append("in transit")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(stock_fields={"return_requested": True})


def _compute_return_dispatched(current: CurrentState, *, central_location_id: int, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if not current.return_requested:
        fail.append("return not requested")
    if not current.stored_at_location:
        fail.append("not stored at location")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields = {
        "return_requested": False,
        "in_transit": True,
        "stored_at_location": False,
        "confirmed_at_location": False,
    }
    if current.has_active_allocation:
        stock_fields["subject_identifier"] = ""
    return StateDelta(
        stock_fields=stock_fields,
        storage_bin_item="delete",
        allocation_action="end" if current.has_active_allocation else "unchanged",
        allocation_end_reason="returned" if current.has_active_allocation else None,
        new_location_id=central_location_id,
    )


def _compute_return_received(current: CurrentState, *, central_location_id: int, **_) -> StateDelta:
    if not current.in_transit:
        return StateDelta(preconditions_failed=("not in transit",))
    return StateDelta(
        stock_fields={"in_transit": False, "confirmed_at_location": False},
        new_location_id=central_location_id,
    )


def _compute_return_disposition_repooled(current: CurrentState, **_) -> StateDelta:
    if current.in_transit:
        return StateDelta(preconditions_failed=("still in transit",))
    return StateDelta(stock_fields={"quarantined": False})


def _compute_return_disposition_quarantined(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.in_transit:
        fail.append("still in transit")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    return StateDelta(stock_fields={"quarantined": True})


def _compute_return_disposition_destroyed(current: CurrentState, **_) -> StateDelta:
    if current.destroyed:
        return StateDelta(preconditions_failed=("already destroyed",))
    if current.in_transit:
        return StateDelta(preconditions_failed=("still in transit",))
    return StateDelta(stock_fields={"destroyed": True, "quarantined": False})


def _compute_adjusted(current: CurrentState, *, unit_qty_delta: Decimal, **_) -> StateDelta:
    return StateDelta(unit_qty_delta=unit_qty_delta)


def _compute_damaged(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.damaged:
        fail.append("already damaged")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"damaged": True}
    if current.stored_at_location:
        stock_fields["stored_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current.has_active_allocation else "unchanged",
        allocation_end_reason="damaged" if current.has_active_allocation else None,
        storage_bin_item="delete" if current.stored_at_location else "unchanged",
    )


def _compute_lost(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if current.damaged:
        fail.append("already damaged — use DAMAGED pathway")
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"lost": True}
    if current.stored_at_location:
        stock_fields["stored_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current.has_active_allocation else "unchanged",
        allocation_end_reason="lost" if current.has_active_allocation else None,
        storage_bin_item="delete" if current.stored_at_location else "unchanged",
    )


def _compute_expired(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"expired": True}
    if current.stored_at_location:
        stock_fields["stored_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current.has_active_allocation else "unchanged",
        allocation_end_reason="expired" if current.has_active_allocation else None,
        storage_bin_item="delete" if current.stored_at_location else "unchanged",
    )


def _compute_voided(current: CurrentState, **_) -> StateDelta:
    fail = _check_not_terminal(current)
    if fail:
        return StateDelta(preconditions_failed=tuple(fail))
    stock_fields: dict = {"voided": True}
    if current.stored_at_location:
        stock_fields["stored_at_location"] = False
    return StateDelta(
        stock_fields=stock_fields,
        allocation_action="end" if current.has_active_allocation else "unchanged",
        allocation_end_reason="voided" if current.has_active_allocation else None,
        storage_bin_item="delete" if current.stored_at_location else "unchanged",
    )


def _compute_reversal(current: CurrentState, **_) -> StateDelta:
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


def compute_delta(txn_type: str, current: CurrentState, **kwargs) -> StateDelta:
    computer = _COMPUTERS.get(txn_type)
    if computer is None:
        raise ValueError(f"Unknown transaction type: {txn_type!r}")
    return computer(current, **kwargs)
