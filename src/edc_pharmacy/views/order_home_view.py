"""Order management — landing page (orders list).

Parallel to ReceiveHomeView but focused on creating and managing orders and
their items, independent of the receive workflow.
"""

from __future__ import annotations

from clinicedc_constants import COMPLETE, PARTIAL
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Order, Receive
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class OrderHomeView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/order_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.select_related("supplier").order_by("-order_datetime")
        receive_order_ids = set(Receive.objects.values_list("order_id", flat=True))
        rows = [
            {
                "order": order,
                "has_receive": order.pk in receive_order_ids,
            }
            for order in orders
        ]
        context["rows"] = rows
        context.update(
            COMPLETE=COMPLETE,
            PARTIAL=PARTIAL,
        )
        return context
