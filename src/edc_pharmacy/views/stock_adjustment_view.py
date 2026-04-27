"""Stock adjustment view (central pharmacist).

Allows the central pharmacist to apply status adjustments (Lost, Damaged,
Expired, Voided) to a batch of scanned stock codes, or a quantity correction
(Adjusted) to a single stock item.  Every change goes through apply_transaction
so the full audit trail is preserved in the StockTransaction ledger.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..exceptions import InvalidTransitionError
from ..models import Stock
from ..transaction_log import apply_transaction
from ..constants import TXN_ADJUSTED, TXN_DAMAGED, TXN_EXPIRED, TXN_LOST, TXN_VOIDED

STATUS_ADJUSTMENT_TYPES = {
    TXN_LOST: "Lost",
    TXN_DAMAGED: "Damaged",
    TXN_EXPIRED: "Expired",
    TXN_VOIDED: "Voided",
}


@method_decorator(login_required, name="dispatch")
class StockAdjustmentView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Central pharmacist: apply status or quantity adjustments to stock."""

    template_name = "edc_pharmacy/stock/stock_adjustments.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        last_code = self.request.GET.get("last_code", "").strip().upper()
        ledger_base = reverse("edc_pharmacy:ledger_url")
        last_ledger_url = f"{ledger_base}?q={last_code}" if last_code else ""
        kwargs.update(
            status_adjustment_types=STATUS_ADJUSTMENT_TYPES,
            last_code=last_code,
            last_ledger_url=last_ledger_url,
        )
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        form_type = request.POST.get("form_type", "").strip()
        if form_type == "status":
            return self._handle_status_adjustment(request)
        if form_type == "qty":
            return self._handle_qty_adjustment(request)
        return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

    # ------------------------------------------------------------------
    # Status adjustment (Lost / Damaged / Expired / Voided)
    # ------------------------------------------------------------------

    def _handle_status_adjustment(self, request):
        codes = [c.strip().upper() for c in request.POST.getlist("codes") if c.strip()]
        adjustment_type = request.POST.get("adjustment_type", "").strip()
        reason = request.POST.get("reason", "").strip()

        if not codes:
            messages.warning(request, "No stock codes submitted.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        if adjustment_type not in STATUS_ADJUSTMENT_TYPES:
            messages.error(request, f"Invalid adjustment type: {adjustment_type!r}")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        if not reason:
            messages.error(request, "A reason is required.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        processed, skipped = [], []
        for code in codes:
            try:
                stock = Stock.objects.get(code=code)
            except Stock.DoesNotExist:
                skipped.append(f"{code} (not found)")
                continue
            try:
                apply_transaction(stock, adjustment_type, request.user, reason=reason)
                processed.append(code)
            except InvalidTransitionError as e:
                skipped.append(f"{code} ({e})")

        label = STATUS_ADJUSTMENT_TYPES.get(adjustment_type, adjustment_type)
        if processed:
            messages.success(
                request,
                f"Marked {len(processed)} item(s) as {label}: {', '.join(processed)}",
            )
        if skipped:
            messages.warning(
                request,
                f"Skipped {len(skipped)} item(s): {', '.join(skipped)}",
            )

        return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

    # ------------------------------------------------------------------
    # Quantity adjustment (Adjusted)
    # ------------------------------------------------------------------

    def _handle_qty_adjustment(self, request):
        code = request.POST.get("code", "").strip().upper()
        reason = request.POST.get("reason", "").strip()
        raw_delta = request.POST.get("unit_qty_delta", "").strip()

        if not code:
            messages.error(request, "A stock code is required.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        if not reason:
            messages.error(request, "A reason is required.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        try:
            unit_qty_delta = Decimal(raw_delta)
        except (InvalidOperation, ValueError):
            messages.error(request, f"Invalid quantity: {raw_delta!r}")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        if unit_qty_delta == 0:
            messages.warning(request, "Delta is zero — nothing to adjust.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        try:
            stock = Stock.objects.get(code=code)
        except Stock.DoesNotExist:
            messages.error(request, f"Stock code {code!r} not found.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_adjustments_url"))

        try:
            apply_transaction(
                stock, TXN_ADJUSTED, request.user,
                reason=reason,
                unit_qty_delta=unit_qty_delta,
            )
            sign = "+" if unit_qty_delta > 0 else ""
            messages.success(
                request,
                f"Quantity adjustment applied to {code}: {sign}{unit_qty_delta}",
            )
        except InvalidTransitionError as e:
            messages.error(request, str(e))

        return HttpResponseRedirect(
            reverse("edc_pharmacy:stock_adjustments_url") + f"?last_code={code}#qty-adjustment"
        )
