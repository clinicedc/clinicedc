"""Stock take scan page.

Shows the expected items for a storage bin and accepts scanned codes.
On POST, compares scanned vs expected and creates StockTake + StockTakeItem
records, then redirects to the results page.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import (
    MATCHED,
    MISSING,
    UNEXPECTED,
    Stock,
    StockTake,
    StockTakeItem,
    StorageBin,
    StorageBinItem,
)


@method_decorator(login_required, name="dispatch")
class StockTakeScanView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Scan page for a single storage bin stock take."""

    template_name = "edc_pharmacy/stock/stock_take_scan.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_storage_bin(self):
        return get_object_or_404(StorageBin, pk=self.kwargs["storage_bin"])

    def get_context_data(self, **kwargs):
        kwargs.pop("storage_bin", None)  # remove UUID kwarg to avoid conflict
        storage_bin = self.get_storage_bin()
        expected_items = (
            StorageBinItem.objects.filter(storage_bin=storage_bin)
            .select_related("stock")
            .order_by("code")
        )
        return super().get_context_data(
            storage_bin=storage_bin,
            expected_items=expected_items,
            expected_count=expected_items.count(),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):  # noqa:ARG002
        storage_bin = self.get_storage_bin()
        scanned_codes = {c.strip().upper() for c in request.POST.getlist("codes") if c.strip()}

        if not scanned_codes:
            messages.warning(request, "No codes scanned.")
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:stock_take_scan_url", kwargs={"storage_bin": storage_bin.pk}
                )
            )

        # Expected codes: all codes registered in this bin
        expected_qs = StorageBinItem.objects.filter(storage_bin=storage_bin).select_related(
            "stock"
        )
        expected_codes = {item.code: item.stock for item in expected_qs}

        matched = scanned_codes & expected_codes.keys()
        missing = expected_codes.keys() - scanned_codes
        unexpected = scanned_codes - expected_codes.keys()

        # Create StockTake header
        stock_take = StockTake.objects.create(
            storage_bin=storage_bin,
            performed_by=request.user,
            expected_count=len(expected_codes),
            scanned_count=len(scanned_codes),
            matched_count=len(matched),
            missing_count=len(missing),
            unexpected_count=len(unexpected),
            status="completed",
            site=storage_bin.location.site or request.site,
        )

        # Build StockTakeItem rows
        items = [
            StockTakeItem(
                stock_take=stock_take,
                stock=expected_codes[code],
                code=code,
                status=MATCHED,
            )
            for code in matched
        ]

        items.extend(
            [
                StockTakeItem(
                    stock_take=stock_take,
                    stock=expected_codes[code],
                    code=code,
                    status=MISSING,
                )
                for code in missing
            ]
        )

        for code in unexpected:
            # Try to find the stock in the system (may not be in this bin)
            try:
                stock = Stock.objects.get(code=code)
            except Stock.DoesNotExist:
                stock = None
            items.append(
                StockTakeItem(
                    stock_take=stock_take,
                    stock=stock,
                    code=code,
                    status=UNEXPECTED,
                )
            )

        StockTakeItem.objects.bulk_create(items)

        messages.success(
            request,
            f"Stock take complete: {len(matched)} matched, "
            f"{len(missing)} missing, {len(unexpected)} unexpected.",
        )
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:stock_take_results_url", kwargs={"stock_take": stock_take.pk}
            )
        )
