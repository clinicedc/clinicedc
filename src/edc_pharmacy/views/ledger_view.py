"""Stock transaction ledger view.

A searchable read-only view of the StockTransaction ledger, scoped to a
stock code or subject identifier.  Intended as the landing point from the
Central Pharmacy home page; links out to the full admin changelist for
deeper filtering/export.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import StockTransaction

MAX_ROWS = 200


@method_decorator(login_required, name="dispatch")
class LedgerView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Read-only ledger search: stock code or subject identifier."""

    template_name = "edc_pharmacy/stock/ledger.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        q = self.request.GET.get("q", "").strip()
        transactions = []
        truncated = False
        qty_total = Decimal(0)
        unit_qty_total = Decimal(0)

        if q:
            qs = StockTransaction.objects.filter(
                Q(stock__code__iexact=q)
                | Q(stock__subject_identifier__icontains=q)
                | Q(to_allocation__registered_subject__subject_identifier__icontains=q)
                | Q(from_allocation__registered_subject__subject_identifier__icontains=q)
            ).select_related(
                "stock",
                "actor",
                "from_location",
                "to_location",
                "from_allocation",
                "to_allocation",
            ).order_by("-transaction_datetime").distinct()

            total = qs.count()
            truncated = total > MAX_ROWS

            # Build row dicts and accumulate totals.
            # Priority: to_allocation → from_allocation → stock.subject_identifier.
            for txn in qs[:MAX_ROWS]:
                alloc = txn.to_allocation or txn.from_allocation
                if alloc and alloc.subject_identifier:
                    subject_identifier = alloc.subject_identifier
                else:
                    subject_identifier = txn.stock.subject_identifier or ""
                qty_total += txn.qty_delta or Decimal(0)
                unit_qty_total += txn.unit_qty_delta or Decimal(0)
                transactions.append({"txn": txn, "subject_identifier": subject_identifier})

        # Build the admin changelist URL, optionally pre-filtered.
        admin_url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransaction_changelist")
        if q:
            admin_url = f"{admin_url}?q={q}"

        kwargs.update(
            q=q,
            transactions=transactions,
            truncated=truncated,
            max_rows=MAX_ROWS,
            admin_url=admin_url,
            qty_total=qty_total,
            unit_qty_total=unit_qty_total,
        )
        return super().get_context_data(**kwargs)
