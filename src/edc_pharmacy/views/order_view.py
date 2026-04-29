"""Order management — per-order page.

Shows the order header + every OrderItem as a panel with [Edit] / [Delete]
actions and an [+ Add item] button.  Receiving lives in a separate workflow
(see ReceiveOrderView).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Order, OrderItem, Receive, ReceiveItem
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class OrderView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/order.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    @staticmethod
    def _build_rows(order):
        zero = Decimal("0.0")
        order_items = (
            OrderItem.objects.filter(order=order)
            .select_related("product", "container")
            .order_by("order_item_identifier")
        )
        # Map order_item_id -> bool indicating any ReceiveItem exists
        received_set = set(
            ReceiveItem.objects.filter(order_item__order=order).values_list(
                "order_item_id", flat=True
            )
        )
        rows = []
        for oi in order_items:
            received = oi.unit_qty_received or zero
            rows.append(
                {
                    "order_item": oi,
                    "can_delete": (received == zero and oi.pk not in received_set),
                }
            )
        return rows

    def get_context_data(self, **kwargs):
        kwargs.pop("order", None)
        context = super().get_context_data(**kwargs)
        order = self.get_order()
        rows = self._build_rows(order)
        has_receive = Receive.objects.filter(order=order).exists()
        context.update(order=order, rows=rows, has_receive=has_receive)
        return context

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        order = self.get_order()
        action = request.POST.get("action")
        if action == "delete_item":
            return self._handle_delete_item(request, order)
        return HttpResponseRedirect(
            reverse("edc_pharmacy:order_url", kwargs={"order": order.pk})
        )

    @staticmethod
    def _handle_delete_item(request, order):
        order_item_pk = request.POST.get("order_item")
        order_item = get_object_or_404(OrderItem, pk=order_item_pk, order=order)
        if (order_item.unit_qty_received or Decimal("0.0")) > Decimal("0.0"):
            messages.error(
                request,
                f"Cannot delete order item {order_item.order_item_identifier}: "
                "stock has already been received against it.",
            )
        else:
            try:
                identifier = order_item.order_item_identifier
                order_item.delete()
                messages.success(request, f"Order item {identifier} deleted.")
            except ProtectedError:
                messages.error(
                    request,
                    f"Cannot delete order item {order_item.order_item_identifier}: "
                    "it is referenced by other records.",
                )
        return HttpResponseRedirect(
            reverse("edc_pharmacy:order_url", kwargs={"order": order.pk})
        )
