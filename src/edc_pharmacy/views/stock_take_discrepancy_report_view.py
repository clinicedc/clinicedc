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
from ..utils import get_related_or_none, last_txn_abbr_by_stock
from .stock_take_conflicts import annotate_conflicts
from .stock_take_site_filter import get_selected_site_id, stock_take_site_choices


@method_decorator(login_required, name="dispatch")
class StockTakeDiscrepancyReportView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_take_discrepancy_report.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        base = StorageBin.objects.filter(in_use=True)

        # Sites the user can choose from: only those with in-use bins. The
        # default ("All sites") leaves the report unfiltered.
        site_choices = stock_take_site_choices(base)
        selected_site_id = get_selected_site_id(self.request, site_choices)

        bins = base.select_related("container", "location")
        if selected_site_id:
            bins = bins.filter(location__site_id=selected_site_id)
        bins = bins.order_by("location__display_name", "bin_identifier")

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
                .select_related(
                    "stock__product",
                    "stock__allocation__registered_subject",
                )
                .order_by("status", "code")
            )
            # Populate the stock_take FK cache so neither conflict annotation nor
            # the template re-queries it per item.
            for item in bin_items:
                item.stock_take = last
            items.extend(bin_items)

        annotate_conflicts(items)
        # Last ledger transaction code per stock, same abbreviations as the PDF.
        txn_abbr = last_txn_abbr_by_stock({item.stock_id for item in items})
        for item in items:
            item.txn_abbr = txn_abbr.get(item.stock_id, "")
            item.subject_identifier = self._subject_identifier(item)
        return super().get_context_data(
            items=items,
            site_choices=site_choices,
            selected_site_id=selected_site_id,
            **kwargs,
        )

    @staticmethod
    def _subject_identifier(item: StockTakeItem) -> str:
        """The allocated subject for the item's stock, or "" if unallocated."""
        stock = item.stock
        if stock and get_related_or_none(stock, "allocation"):
            return stock.allocation.registered_subject.subject_identifier or ""
        return ""
