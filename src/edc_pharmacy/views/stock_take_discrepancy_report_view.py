"""Stock take discrepancy report.

Shows only bins whose most recent stock take has missing or unexpected items,
grouped by location.

Each discrepancy is annotated with a cross-bin *conflict* hint so the user does
not, for example, mark an item Lost when it is actually sitting in another bin
as an unexpected scan.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..choices import STOCK_TRANSACTION_ABBR, STOCK_TRANSACTION_CHOICES
from ..models import MISSING, UNEXPECTED, StockTake, StockTakeItem, StorageBin
from ..utils import last_txn_abbr_by_stock, subject_identifier_by_stock
from .stock_take_conflicts import annotate_conflicts
from .stock_take_site_filter import get_selected_site_id, stock_take_site_choices

# "Resolved" here means handled — either corrected (a linked ledger
# transaction) or acknowledged — matching StockTakeItem.handled.
RESOLVED = "resolved"
UNRESOLVED = "unresolved"
RESOLVED_CHOICES = ((RESOLVED, "Resolved"), (UNRESOLVED, "Unresolved"))


@dataclass(frozen=True)
class TxnChoice:
    """A selectable last-transaction abbreviation for the TXN filter."""

    abbr: str
    display_name: str


def _txn_choices(items: list[StockTakeItem]) -> list[TxnChoice]:
    """TXN abbreviations present among ``items``, with their full labels."""
    abbr_to_type = {abbr: txn_type for txn_type, abbr in STOCK_TRANSACTION_ABBR.items()}
    txn_display = dict(STOCK_TRANSACTION_CHOICES)
    abbrs = {item.txn_abbr for item in items if item.txn_abbr}
    choices = [
        TxnChoice(abbr, txn_display.get(abbr_to_type.get(abbr), abbr)) for abbr in abbrs
    ]
    return sorted(choices, key=lambda choice: choice.abbr)


def _get_selected_txn(request: WSGIRequest, txn_choices: list[TxnChoice]) -> str:
    """Return the chosen TXN abbreviation from ``?txn=``, or "" for "All"."""
    raw = request.GET.get("txn", "").strip().upper()
    valid_abbrs = {choice.abbr for choice in txn_choices}
    return raw if raw in valid_abbrs else ""


def _get_selected_resolved(request: WSGIRequest) -> str:
    """Return the chosen resolution state from ``?resolved=``, or "" for "All"."""
    raw = request.GET.get("resolved", "").strip().lower()
    return raw if raw in (RESOLVED, UNRESOLVED) else ""


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
                .select_related("stock__product")
                .order_by("status", "code")
            )
            # Populate the stock_take FK cache so neither conflict annotation nor
            # the template re-queries it per item.
            for item in bin_items:
                item.stock_take = last
            items.extend(bin_items)

        annotate_conflicts(items)
        # Per-stock lookups (one query each), same sources as the PDF.
        stock_ids = {item.stock_id for item in items}
        txn_abbr = last_txn_abbr_by_stock(stock_ids)
        subject = subject_identifier_by_stock(stock_ids)
        for item in items:
            item.txn_abbr = txn_abbr.get(item.stock_id, "")
            item.subject_identifier = subject.get(item.stock_id, "")

        # TXN and resolved/unresolved filters, applied after the lookups above
        # so the TXN choices reflect the current site selection.
        txn_choices = _txn_choices(items)
        selected_txn = _get_selected_txn(self.request, txn_choices)
        selected_resolved = _get_selected_resolved(self.request)
        if selected_txn:
            items = [item for item in items if item.txn_abbr == selected_txn]
        if selected_resolved == RESOLVED:
            items = [item for item in items if item.handled]
        elif selected_resolved == UNRESOLVED:
            items = [item for item in items if not item.handled]

        return super().get_context_data(
            items=items,
            site_choices=site_choices,
            selected_site_id=selected_site_id,
            txn_choices=txn_choices,
            selected_txn=selected_txn,
            resolved_choices=RESOLVED_CHOICES,
            selected_resolved=selected_resolved,
            **kwargs,
        )
