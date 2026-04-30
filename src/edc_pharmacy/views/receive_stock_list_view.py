"""Receive workflow — read-only DataTable of all Stock records received
against this order.

URL:  /receive/<order>/stock/   name: receive_stock_list_url
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..models import Order, Receive, Stock
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class ReceiveStockListView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/receive_stock_list.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        kwargs.pop("order", None)
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        show_batch = PHARMACIST_ROLE in roles

        order = self._get_order()
        receive = self._get_receive(order)
        stocks = (
            Stock.objects.filter(receive_item__receive=receive)
            .select_related(
                "product", "lot", "container", "location", "receive_item__order_item"
            )
            .order_by("-stock_datetime")
            if receive
            else Stock.objects.none()
        )
        context.update(
            order=order,
            receive=receive,
            stocks=stocks,
            confirmed_count=stocks.filter(confirmed=True).count() if receive else 0,
            unconfirmed_count=stocks.filter(confirmed=False).count() if receive else 0,
            show_batch=show_batch,
        )
        return context

    def _get_order(self):
        from django.shortcuts import get_object_or_404

        return get_object_or_404(Order, pk=self.kwargs["order"])

    @staticmethod
    def _get_receive(order):
        try:
            return Receive.objects.get(order=order)
        except Receive.DoesNotExist:
            return None
