"""Utilities for the stock-return workflow.

Each function is a thin wrapper that:
  1. Looks up the relevant Stock objects.
  2. Calls apply_transaction() for the appropriate TXN_RETURN_* type.
  3. Creates or updates the ReturnItem business object where needed.

The six lifecycle steps are:

  TXN_RETURN_REQUESTED      - site flags stock for return
  TXN_RETURN_DISPATCHED     - site ships stock back to central
  TXN_RETURN_RECEIVED       - central confirms receipt
  TXN_RETURN_DISPOSITION_REPOOLED     - returned stock re-enters general supply
  TXN_RETURN_DISPOSITION_QUARANTINED  - returned stock quarantined
  TXN_RETURN_DISPOSITION_DESTROYED    - returned stock destroyed
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db import transaction

from ..constants import (
    CENTRAL_LOCATION,
    TXN_RETURN_DISPATCHED,
    TXN_RETURN_DISPOSITION_DESTROYED,
    TXN_RETURN_DISPOSITION_QUARANTINED,
    TXN_RETURN_DISPOSITION_REPOOLED,
    TXN_RETURN_RECEIVED,
    TXN_RETURN_REQUESTED,
)
from ..exceptions import ReturnError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from ..models import Location, ReturnRequest, Stock


# ---------------------------------------------------------------------------
# Step 1 — Request
# ---------------------------------------------------------------------------

def request_stock_return(
    stock_codes: list[str],
    actor: AbstractUser,
    *,
    reason: str = "return requested",
) -> tuple[list[str], list[str]]:
    """Mark each stock code as return_requested.

    Returns (requested_codes, skipped_codes).
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    requested, skipped = [], []
    for code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(code=code, invalid_state=False)
        except stock_model_cls.DoesNotExist:
            skipped.append(code)
            continue
        with transaction.atomic():
            txn = apply_transaction(stock, TXN_RETURN_REQUESTED, actor, reason=reason)
        if txn:
            requested.append(code)
    return requested, skipped


# ---------------------------------------------------------------------------
# Step 2 — Dispatch
# ---------------------------------------------------------------------------

def dispatch_return(
    return_request: ReturnRequest,
    stock_codes: list[str],
    actor: AbstractUser,
    *,
    reason: str = "return dispatched",
) -> tuple[list[str], list[str]]:
    """Dispatch stock items from site back to central.

    Creates a ReturnItem for each code and fires TXN_RETURN_DISPATCHED.
    Returns (dispatched_codes, skipped_codes).
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    return_item_model_cls = django_apps.get_model("edc_pharmacy.returnitem")
    location_model_cls: type[Location] = django_apps.get_model("edc_pharmacy.location")

    try:
        central_location = location_model_cls.objects.get(name=CENTRAL_LOCATION)
    except location_model_cls.DoesNotExist:
        raise ReturnError(f"Central location '{CENTRAL_LOCATION}' not found.")

    dispatched, skipped = [], []
    for code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=code,
                invalid_state=False,
                return_requested=True,
                location=return_request.from_location,
            )
        except stock_model_cls.DoesNotExist:
            skipped.append(code)
            continue
        with transaction.atomic():
            return_item = return_item_model_cls.objects.create(
                stock=stock,
                return_request=return_request,
                user_created=actor.username,
            )
            apply_transaction(
                stock,
                TXN_RETURN_DISPATCHED,
                actor,
                central_location_id=central_location.id,
                return_item=return_item,
                reason=reason,
            )
        dispatched.append(code)
    return dispatched, skipped


# ---------------------------------------------------------------------------
# Step 3 — Receive
# ---------------------------------------------------------------------------

def receive_return(
    return_request: ReturnRequest,
    stock_codes: list[str],
    actor: AbstractUser,
    *,
    reason: str = "return received",
) -> tuple[list[str], list[str]]:
    """Central confirms receipt of returned stock.

    Returns (received_codes, skipped_codes).
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    location_model_cls: type[Location] = django_apps.get_model("edc_pharmacy.location")

    try:
        central_location = location_model_cls.objects.get(name=CENTRAL_LOCATION)
    except location_model_cls.DoesNotExist:
        raise ReturnError(f"Central location '{CENTRAL_LOCATION}' not found.")

    received, skipped = [], []
    for code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=code,
                invalid_state=False,
                in_transit=True,
                returnitem__return_request=return_request,
            )
        except stock_model_cls.DoesNotExist:
            skipped.append(code)
            continue
        with transaction.atomic():
            apply_transaction(
                stock,
                TXN_RETURN_RECEIVED,
                actor,
                central_location_id=central_location.id,
                reason=reason,
            )
        received.append(code)
    return received, skipped


# ---------------------------------------------------------------------------
# Step 4 — Disposition
# ---------------------------------------------------------------------------

def disposition_return(
    stock_codes: list[str],
    actor: AbstractUser,
    *,
    disposition: str,
    reason: str = "",
) -> tuple[list[str], list[str]]:
    """Apply final disposition to returned stock.

    disposition must be one of:
      'repooled', 'quarantined', 'destroyed'

    Returns (processed_codes, skipped_codes).
    """
    _disposition_map = {
        "repooled": TXN_RETURN_DISPOSITION_REPOOLED,
        "quarantined": TXN_RETURN_DISPOSITION_QUARANTINED,
        "destroyed": TXN_RETURN_DISPOSITION_DESTROYED,
    }
    txn_type = _disposition_map.get(disposition)
    if txn_type is None:
        raise ReturnError(
            f"Invalid disposition {disposition!r}. "
            f"Choose from: {', '.join(_disposition_map)}"
        )

    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    processed, skipped = [], []
    for code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(code=code, invalid_state=False)
        except stock_model_cls.DoesNotExist:
            skipped.append(code)
            continue
        with transaction.atomic():
            apply_transaction(
                stock,
                txn_type,
                actor,
                reason=reason or f"disposition: {disposition}",
            )
        processed.append(code)
    return processed, skipped


__all__ = [
    "dispatch_return",
    "disposition_return",
    "receive_return",
    "request_stock_return",
]
