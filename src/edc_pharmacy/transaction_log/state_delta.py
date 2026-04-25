from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal

ChildAction = Literal["create", "delete", "replace", "unchanged"]
AllocationAction = Literal["create", "end", "unchanged"]


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
    damaged: bool
    lost: bool
    expired: bool
    voided: bool
    return_requested: bool
    quarantined: bool
    qty_in: Decimal
    qty_out: Decimal
    unit_qty_in: Decimal
    unit_qty_out: Decimal
    container_unit_qty: Decimal
    has_active_allocation: bool
    active_allocation_subject: str
    has_storage_bin_item: bool
    has_confirmation_at_location_item: bool


@dataclass(frozen=True)
class StateDelta:
    # Absolute field values to apply to Stock (not deltas).
    stock_fields: dict[str, Any] = field(default_factory=dict)

    # OneToOne child row lifecycle per transaction.
    # "replace" = delete existing then create new (used by BIN_MOVED).
    storage_bin_item: ChildAction = "unchanged"
    confirmation_at_location_item: ChildAction = "unchanged"
    confirmation: ChildAction = "unchanged"
    dispense_item: ChildAction = "unchanged"

    # Allocation lifecycle.
    allocation_action: AllocationAction = "unchanged"
    allocation_end_reason: str | None = None

    # New location FK id (None = no change).
    new_location_id: int | None = None

    # Signed quantity deltas (None = no change).
    qty_delta: Decimal | None = None
    unit_qty_delta: Decimal | None = None

    # Non-empty = compute_delta found the transition illegal; apply_transaction raises.
    preconditions_failed: tuple[str, ...] = ()
