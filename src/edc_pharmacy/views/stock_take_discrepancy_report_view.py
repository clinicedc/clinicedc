"""Stock take discrepancy report.

Shows only bins whose most recent stock take has missing or unexpected items,
grouped by location.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import MISSING, UNEXPECTED, StockTake, StorageBin


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

        # Build per-bin rows, keeping only those with discrepancies
        rows_by_location: dict[str, list[dict]] = {}
        for b in bins:
            last = (
                StockTake.objects.filter(storage_bin=b)
                .order_by("-stock_take_datetime")
                .first()
            )
            if not last or (last.missing_count == 0 and last.unexpected_count == 0):
                continue

            missing_items = list(
                last.items.filter(status=MISSING).select_related("stock__product").order_by("code")
            )
            unexpected_items = list(
                last.items.filter(status=UNEXPECTED)
                .select_related("stock__product")
                .order_by("code")
            )

            location_name = last.storage_bin.location.display_name or last.storage_bin.location.name
            rows_by_location.setdefault(location_name, []).append(
                {
                    "bin": b,
                    "stock_take": last,
                    "missing": missing_items,
                    "unexpected": unexpected_items,
                }
            )

        return super().get_context_data(rows_by_location=rows_by_location, **kwargs)
