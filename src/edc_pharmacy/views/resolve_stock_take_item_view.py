"""Resolve a single stock take discrepancy.

A stock take only *reports* discrepancies. This endpoint applies the
appropriate correction to one ``StockTakeItem`` and records an auditable link
from the item to the resulting ``StockTransaction`` ledger row.

Allowed actions depend on the item's status:

* **missing**    — mark the stock Lost / Damaged / Expired (status adjustment).
* **unexpected** — move the stock into this bin (``TXN_BIN_MOVED``).

A *matched* item, or an *unexpected* item whose code is not in the system
(``stock is None``), cannot be resolved here.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
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

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        item = get_object_or_404(StockTakeItem, pk=kwargs["stock_take_item"])
        action = request.POST.get("action", "").strip().lower()
        reason = request.POST.get("reason", "").strip()

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
