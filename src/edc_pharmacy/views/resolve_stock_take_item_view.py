"""Resolve a single stock take discrepancy.

A stock take only *reports* discrepancies. This endpoint applies the
appropriate correction to one ``StockTakeItem`` and records an auditable link
from the item to the resulting ``StockTransaction`` ledger row.

Allowed actions depend on the item's status:

* **missing**    — mark the stock Lost / Damaged / Expired (status adjustment).
* **unexpected** — add the stock to this bin (``TXN_BIN_MOVED``).

A *matched* item, or an *unexpected* item whose code is not in the system
(``stock is None``), cannot be resolved here.

The ``undo`` action reverses an "add to bin" resolution: it returns the item to
its original bin via a compensating ``TXN_BIN_MOVED`` and re-opens the
discrepancy. Only available for an unexpected item resolved by a bin move.

The ``acknowledge`` action records a review note (no transaction) for an
unexpected item that cannot be corrected in-system — not in the system, or in a
terminal state such as dispensed — so the row can be cleared. ``unacknowledge``
reverses it.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from ..constants import TXN_BIN_MOVED, TXN_DAMAGED, TXN_EXPIRED, TXN_LOST
from ..exceptions import InvalidTransitionError
from ..models import MISSING, UNEXPECTED, StockTakeItem
from ..transaction_log import apply_transaction

# Status-adjustment actions allowed for a *missing* item.
MISSING_ACTIONS = {
    "lost": TXN_LOST,
    "damaged": TXN_DAMAGED,
    "expired": TXN_EXPIRED,
}

# The single action allowed for an *unexpected* item.
MOVE_ACTION = "move_to_bin"

# Reverse a prior "add to bin" resolution.
UNDO_ACTION = "undo"

# Acknowledge an unexpected item that cannot be corrected in-system, and reverse it.
ACK_ACTION = "acknowledge"
UNACK_ACTION = "unacknowledge"


@method_decorator(login_required, name="dispatch")
class ResolveStockTakeItemView(View):
    """Apply a correction to one stock take discrepancy and link the ledger row."""

    def _redirect(self, request):
        next_url = request.POST.get("next", "").strip()
        if next_url:
            return HttpResponseRedirect(next_url)
        return HttpResponseRedirect(
            reverse("edc_pharmacy:stock_take_discrepancy_report_url")
        )

    def _status_params(self, request, item, action, reason) -> tuple | None:
        """Map (item status, action) to ``(txn_type, apply_kwargs)``.

        Adds a user message and returns ``None`` for an invalid combination.
        """
        if item.status == MISSING:
            txn_type = MISSING_ACTIONS.get(action)
            if not txn_type:
                messages.error(request, f"Invalid action for a missing item: {action!r}")
                return None
            if not reason:
                # The pharmacist chooses lost/damaged/expired, so a note is required.
                messages.error(request, "A reason is required.")
                return None
            return txn_type, {"reason": reason}
        if item.status == UNEXPECTED:
            if action != MOVE_ACTION:
                messages.error(
                    request, f"Invalid action for an unexpected item: {action!r}"
                )
                return None
            # Adding a scanned item to the bin it was counted in always has the
            # same meaning, so the audit note is generated rather than prompted.
            storage_bin = item.stock_take.storage_bin
            return TXN_BIN_MOVED, {
                "reason": (
                    f"Added to bin {storage_bin.bin_identifier} during stock take "
                    f"{item.stock_take.stock_take_identifier}"
                ),
                "storage_bin": storage_bin,
            }
        messages.error(request, f"{item.code} ({item.status}) cannot be resolved.")
        return None

    def _handle_undo(self, request, item):
        """Reverse an 'add to bin' resolution and re-open the discrepancy."""
        if not item.resolved:
            messages.warning(request, f"{item.code} is not resolved.")
            return self._redirect(request)
        txn = item.stock_transaction
        if txn.transaction_type != TXN_BIN_MOVED:
            messages.error(request, f"{item.code} cannot be undone here.")
            return self._redirect(request)
        origin_bin = txn.from_bin
        if origin_bin is None:
            messages.error(
                request, f"Cannot undo {item.code}: its original bin is unknown."
            )
            return self._redirect(request)
        with transaction.atomic():
            try:
                apply_transaction(
                    item.stock,
                    TXN_BIN_MOVED,
                    request.user,
                    storage_bin=origin_bin,
                    reason=(
                        f"Undo: returned to bin {origin_bin.bin_identifier} "
                        f"(stock take {item.stock_take.stock_take_identifier})"
                    ),
                )
            except InvalidTransitionError as e:
                messages.error(request, f"Could not undo {item.code}: {e}")
                return self._redirect(request)
            item.stock_transaction = None
            item.save(update_fields=["stock_transaction"])
        messages.success(
            request, f"Undone: {item.code} returned to bin {origin_bin.bin_identifier}."
        )
        return self._redirect(request)

    def _handle_acknowledge(self, request, item, note):
        """Record a review note for an unexpected item that can't be corrected."""
        if item.handled:
            messages.warning(request, f"{item.code} is already handled.")
            return self._redirect(request)
        if not (item.status == UNEXPECTED and (item.stock is None or item.stock.is_terminal)):
            messages.error(
                request, f"{item.code} cannot be acknowledged; resolve it instead."
            )
            return self._redirect(request)
        if not note:
            messages.error(request, "A note is required to acknowledge.")
            return self._redirect(request)
        item.acknowledged_datetime = timezone.now()
        item.acknowledged_by = request.user
        item.acknowledged_note = note
        item.save(
            update_fields=[
                "acknowledged_datetime",
                "acknowledged_by",
                "acknowledged_note",
            ]
        )
        messages.success(request, f"Acknowledged {item.code}.")
        return self._redirect(request)

    def _handle_unacknowledge(self, request, item):
        """Reverse an acknowledgement and re-open the discrepancy."""
        if not item.acknowledged:
            messages.warning(request, f"{item.code} is not acknowledged.")
            return self._redirect(request)
        item.acknowledged_datetime = None
        item.acknowledged_by = None
        item.acknowledged_note = ""
        item.save(
            update_fields=[
                "acknowledged_datetime",
                "acknowledged_by",
                "acknowledged_note",
            ]
        )
        messages.success(request, f"Re-opened {item.code}.")
        return self._redirect(request)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        item = get_object_or_404(StockTakeItem, pk=kwargs["stock_take_item"])
        action = request.POST.get("action", "").strip().lower()
        reason = request.POST.get("reason", "").strip()

        handlers = {
            UNDO_ACTION: lambda: self._handle_undo(request, item),
            ACK_ACTION: lambda: self._handle_acknowledge(request, item, reason),
            UNACK_ACTION: lambda: self._handle_unacknowledge(request, item),
        }
        if action in handlers:
            return handlers[action]()

        if item.resolved:
            messages.warning(request, f"{item.code} is already resolved.")
            return self._redirect(request)
        if item.stock is None:
            messages.error(
                request,
                f"{item.code} is not in the system and cannot be resolved here.",
            )
            return self._redirect(request)

        params = self._status_params(request, item, action, reason)
        if params is None:
            return self._redirect(request)
        txn_type, apply_kwargs = params

        with transaction.atomic():
            try:
                txn = apply_transaction(item.stock, txn_type, request.user, **apply_kwargs)
            except InvalidTransitionError as e:
                messages.error(request, f"Could not resolve {item.code}: {e}")
                return self._redirect(request)
            item.stock_transaction = txn
            item.save(update_fields=["stock_transaction"])

        messages.success(request, f"Resolved {item.code} ({item.status}).")
        return self._redirect(request)
