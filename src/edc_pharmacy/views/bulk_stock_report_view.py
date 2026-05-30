"""Bulk container unit-qty report.

Shows all root stock items (from_stock=None) — the large containers that
are received and repacked, not dispensed directly to patients.  Provides
unit_qty_in / unit_qty_out / balance per container so the pharmacist can
audit how many tablet-units have been consumed and how many remain.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Stock
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class BulkStockReportView(
    AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    """Unit-qty in/out/balance report for bulk (non-dispensing) containers."""

    template_name = "edc_pharmacy/stock/bulk_stock_report.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        qs = (
            Stock.objects.filter(
                from_stock__isnull=True,
                container__may_request_as=False,
                container__may_dispense_as=False,
            )
            .select_related(
                "lot__assignment",
                "product__formulation",
                "container",
                "location",
            )
            .annotate(repack_count=Count("repack_requests", distinct=True))
            .order_by("lot__lot_no", "code")
        )

        ledger_base = reverse("edc_pharmacy:ledger_url")

        rows = []
        total_in = Decimal(0)
        total_out = Decimal(0)
        for stock in qs:
            unit_in = stock.unit_qty_in or Decimal(0)
            unit_out = stock.unit_qty_out or Decimal(0)
            balance = unit_in - unit_out
            total_in += unit_in
            total_out += unit_out
            rows.append(
                {
                    "stock": stock,
                    "unit_qty_in": unit_in,
                    "unit_qty_out": unit_out,
                    "balance": balance,
                    "repack_count": stock.repack_count,
                    "ledger_url": f"{ledger_base}?q={stock.code}",
                }
            )

        totals = {
            "unit_qty_in": total_in,
            "unit_qty_out": total_out,
            "balance": total_in - total_out,
        }

        return super().get_context_data(rows=rows, totals=totals, **kwargs)
