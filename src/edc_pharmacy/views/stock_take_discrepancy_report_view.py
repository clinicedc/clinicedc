"""Stock take discrepancy report.

Shows only bins whose most recent stock take has missing or unexpected items,
grouped by location.

Each discrepancy is annotated with a cross-bin *conflict* hint so the user does
not, for example, mark an item Lost when it is actually sitting in another bin
as an unexpected scan.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import MISSING, UNEXPECTED, StockTake, StockTakeItem, StorageBin
from .stock_take_conflicts import annotate_conflicts


@method_decorator(login_required, name="dispatch")
class StockTakeDiscrepancyReportView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_take_discrepancy_report.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        bins = (
            StorageBin.objects.filter(in_use=True)
            .select_related("container", "location")
            .order_by("location__display_name", "bin_identifier")
        )

        # One flat, bin-ordered list of discrepancies (missing then unexpected
        # within each bin) for a single grouped DataTable.
        items: list[StockTakeItem] = []
        for b in bins:
            last = (
                StockTake.objects.filter(storage_bin=b)
                .order_by("-stock_take_datetime")
                .first()
            )
            if not last or (last.missing_count == 0 and last.unexpected_count == 0):
                continue
            # Reuse the already-loaded bin (with container/location) for URLs.
            last.storage_bin = b

            bin_items = list(
                last.items.filter(status__in=(MISSING, UNEXPECTED))
                .select_related("stock__product")
                .order_by("status", "code")
            )
            # Populate the stock_take FK cache so neither conflict annotation nor
            # the template re-queries it per item.
            for item in bin_items:
                item.stock_take = last
            items.extend(bin_items)

        annotate_conflicts(items)
        return super().get_context_data(items=items, **kwargs)
