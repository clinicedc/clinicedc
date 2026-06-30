"""Stock take results page."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import MATCHED, MISSING, UNEXPECTED, StockTake
from .stock_take_conflicts import annotate_conflicts


@method_decorator(login_required, name="dispatch")
class StockTakeResultsView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Results page for a completed stock take."""

    template_name = "edc_pharmacy/stock/stock_take_results.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        kwargs.pop("stock_take", None)  # remove UUID kwarg to avoid conflict
        stock_take = get_object_or_404(StockTake, pk=self.kwargs["stock_take"])
        items = list(stock_take.items.select_related("stock").order_by("status", "code"))
        # Cache the stock_take FK so conflict annotation does not re-query it.
        for item in items:
            item.stock_take = stock_take

        matched = [i for i in items if i.status == MATCHED]
        missing = [i for i in items if i.status == MISSING]
        unexpected = [i for i in items if i.status == UNEXPECTED]
        # Annotate missing/unexpected so the page matches the discrepancy report
        # (e.g. a missing item registered elsewhere is acknowledged, not lost).
        annotate_conflicts(missing + unexpected)

        return super().get_context_data(
            stock_take=stock_take,
            matched=matched,
            missing=missing,
            unexpected=unexpected,
            **kwargs,
        )
