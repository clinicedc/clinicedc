"""Lot-centric stock list — every Stock record derived from a given Lot,
across all orders and receives.

URL:  /lot/<lot>/stock/   name: lot_stock_list_url
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Lot, Stock
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class LotStockListView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/lot_stock_list.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        kwargs.pop("lot", None)
        context = super().get_context_data(**kwargs)
        lot = get_object_or_404(
            Lot.objects.select_related("product", "assignment"),
            pk=self.kwargs["lot"],
        )
        stocks = (
            Stock.objects.filter(lot=lot)
            .select_related(
                "container",
                "location",
                "receive_item__receive",
                "receive_item__order_item__order",
            )
            .order_by("-stock_datetime")
        )
        context.update(
            lot=lot,
            stocks=stocks,
            confirmed_count=stocks.filter(confirmed=True).count(),
            unconfirmed_count=stocks.filter(confirmed=False).count(),
        )
        return context
