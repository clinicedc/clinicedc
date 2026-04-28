"""Stock take landing page.

Lists all active storage bins with their current item count, last stock take
date and outcome summary.  A [Start] button opens the scan page for that bin.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, OuterRef, Prefetch, Subquery
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import StorageBin, StorageBinItem, StockTake


@method_decorator(login_required, name="dispatch")
class StockTakeHomeView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Landing page: list bins with item count and last stock take summary."""

    template_name = "edc_pharmacy/stock/stock_take_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        bins = (
            StorageBin.objects.filter(in_use=True)
            .select_related("container", "location")
            .annotate(item_count=Count("storagebinitem", distinct=True))
            .order_by("location__display_name", "bin_identifier")
        )

        # Last stock take per bin
        last_take_qs = (
            StockTake.objects.filter(storage_bin=OuterRef("pk"))
            .order_by("-stock_take_datetime")
            .values("stock_take_datetime", "status",
                    "matched_count", "missing_count", "unexpected_count")[:1]
        )

        rows = []
        for b in bins:
            last = (
                StockTake.objects.filter(storage_bin=b)
                .order_by("-stock_take_datetime")
                .first()
            )
            rows.append({
                "bin": b,
                "last_take": last,
            })

        return super().get_context_data(rows=rows, **kwargs)
