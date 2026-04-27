"""Stock-transfer landing page.

Lists all StockTransfers (newest first) with scanned-vs-planned progress so
the central pharmacist can see at a glance which transfers still need items
scanned and jump straight into the scan workflow.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import StockTransfer

MAX_TRANSFERS = 100


@method_decorator(login_required, name="dispatch")
class StockTransferHomeView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Landing page for the transfer-stock workflow."""

    template_name = "edc_pharmacy/stock/stock_transfer_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        qs = (
            StockTransfer.objects.annotate(scanned_count=Count("stocktransferitem"))
            .order_by("-transfer_identifier")[:MAX_TRANSFERS]
        )
        transfers = [
            {
                "obj": t,
                "scanned_count": t.scanned_count,
                "remaining": max(0, t.item_count - t.scanned_count),
                "complete": t.scanned_count >= t.item_count,
            }
            for t in qs
        ]
        return super().get_context_data(transfers=transfers, **kwargs)
