"""Receive workflow — landing page.

Lists all orders with their `receive` status so the pharmacist can see
at a glance which orders still have pending items and jump directly to
the per-order receive page.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..models import Order, OrderItem, Receive, ReceiveItem
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class ReceiveHomeView(
    AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/receive_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        if PHARMACIST_ROLE not in roles:
            messages.warning(
                self.request,
                "Batch numbers are hidden. "
                f"You need the {PHARMACIST_ROLE} role to view batch numbers.",
            )
        # Orders table
        rows = []
        orders = Order.objects.select_related("supplier").order_by("-order_datetime")
        receive_map = {r.order_id: r for r in Receive.objects.select_related("supplier").all()}
        for order in orders:
            receive = receive_map.get(order.pk)
            item_count = (
                ReceiveItem.objects.filter(order_item__order=order).count() if receive else 0
            )
            rows.append(
                {
                    "order": order,
                    "receive": receive,
                    "receive_item_count": item_count,
                }
            )

        # Pending order items — all items with outstanding units, regardless of
        # whether a `receive` record exists yet.  The template chooses the right
        # button based on whether a `receive` record is present.
        orders_with_receive = set(receive_map.keys())
        # NULL means the signal hasn't run yet — treat as pending
        pending_order_items = (
            OrderItem.objects.filter(
                Q(unit_qty_pending__gt=0) | Q(unit_qty_pending__isnull=True)
            )
            .select_related("order", "order__supplier", "product", "container")
            .order_by("order__order_datetime", "order_item_identifier")
        )
        pending_rows = [
            {
                "order_item": oi,
                "has_receive": oi.order_id in orders_with_receive,
            }
            for oi in pending_order_items
        ]

        context["rows"] = rows
        context["pending_rows"] = pending_rows
        return context
