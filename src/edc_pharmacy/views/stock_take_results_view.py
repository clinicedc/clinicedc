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


@method_decorator(login_required, name="dispatch")
class StockTakeResultsView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Results page for a completed stock take."""

    template_name = "edc_pharmacy/stock/stock_take_results.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        stock_take = get_object_or_404(StockTake, pk=self.kwargs["stock_take"])
        items = stock_take.items.select_related("stock").order_by("status", "code")

        matched = [i for i in items if i.status == MATCHED]
        missing = [i for i in items if i.status == MISSING]
        unexpected = [i for i in items if i.status == UNEXPECTED]

        return super().get_context_data(
            stock_take=stock_take,
            matched=matched,
            missing=missing,
            unexpected=unexpected,
            **kwargs,
        )
