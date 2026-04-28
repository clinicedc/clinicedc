"""Receive workflow — dedicated page for adding a ReceiveItem.

URL: /receive/<order>/<order_item>/
On success, redirects back to the order page anchored to the order-item panel.
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

from ..auth_objects import PHARMACIST_ROLE
from ..forms.stock import ReceiveItemAddForm
from ..models import Order, OrderItem, Receive, ReceiveItem, Stock
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class ReceiveOrderItemView(
    AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/receive_order_item.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def _get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    def _get_order_item(self, order):
        return get_object_or_404(OrderItem, pk=self.kwargs["order_item"], order=order)

    def _get_receive_item(self, order_item):
        receive_item_pk = self.kwargs.get("receive_item")
        if receive_item_pk:
            return get_object_or_404(
                ReceiveItem, pk=receive_item_pk, order_item=order_item
            )
        return None

    def _get_receive(self, order):
        try:
            return Receive.objects.get(order=order)
        except Receive.DoesNotExist:
            return None

    def _order_url(self, order, order_item=None):
        url = reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
        if order_item:
            url += f"#oi_{order_item.pk}"
        return url

    def get_context_data(self, order=None, order_item=None, form=None, **kwargs):
        kwargs.pop("order", None)
        kwargs.pop("order_item", None)
        kwargs.pop("receive_item", None)
        context = super().get_context_data(**kwargs)

        roles = context.get("roles", [])
        show_batch = PHARMACIST_ROLE in roles
        if not show_batch:
            messages.warning(
                self.request,
                "Batch numbers are hidden. "
                f"You need the {PHARMACIST_ROLE} role to view batch numbers.",
            )

        order = order or self._get_order()
        order_item = order_item or self._get_order_item(order)
        receive_item = self._get_receive_item(order_item)
        receive = self._get_receive(order)

        existing_items = (
            ReceiveItem.objects.filter(order_item=order_item)
            .select_related("lot", "container")
            .order_by("receive_item_datetime")
        )

        if form is None:
            if receive_item is not None:
                form = ReceiveItemAddForm(
                    order_item=order_item,
                    instance=receive_item,
                )
            else:
                form = ReceiveItemAddForm(
                    order_item=order_item,
                    initial={
                        "container": order_item.container,
                        "container_unit_qty": order_item.container_unit_qty,
                        "reference": "-",
                    },
                )

        context.update(
            order=order,
            order_item=order_item,
            receive_item=receive_item,
            receive=receive,
            existing_items=existing_items,
            form=form,
            show_batch=show_batch,
        )
        return context

    def post(self, request, *args, **kwargs):
        order = self._get_order()
        order_item = self._get_order_item(order)
        receive_item = self._get_receive_item(order_item)
        receive = self._get_receive(order)

        if not receive:
            messages.error(request, "Save the receive record before adding items.")
            return HttpResponseRedirect(self._order_url(order, order_item))

        # Editing is locked once any associated Stock has been confirmed.
        if receive_item is not None and Stock.objects.filter(
            receive_item=receive_item, confirmed=True
        ).exists():
            messages.error(
                request,
                f"Cannot edit {receive_item.receive_item_identifier}: "
                "stock has already been confirmed.",
            )
            return HttpResponseRedirect(self._order_url(order, order_item))

        form = ReceiveItemAddForm(
            request.POST, order_item=order_item, instance=receive_item
        )
        if form.is_valid():
            cd = form.cleaned_data
            if receive_item is None:
                ReceiveItem.objects.create(
                    receive=receive,
                    order_item=order_item,
                    lot=cd["lot"],
                    container=cd["container"],
                    container_unit_qty=cd["container_unit_qty"],
                    item_qty_received=cd["item_qty_received"],
                    reference=cd.get("reference") or "-",
                    user_created=request.user.username,
                    user_modified=request.user.username,
                )
                messages.success(
                    request,
                    f"Added {cd['item_qty_received']} × {cd['container']} "
                    f"(batch {cd['lot'].lot_no}).",
                )
            else:
                # Edit: clear existing (unconfirmed) Stock so it can be re-created
                # cleanly by the post_save signal with the new attributes / count.
                Stock.objects.filter(
                    receive_item=receive_item, confirmed=False
                ).delete()
                receive_item.lot = cd["lot"]
                receive_item.container = cd["container"]
                receive_item.container_unit_qty = cd["container_unit_qty"]
                receive_item.item_qty_received = cd["item_qty_received"]
                receive_item.reference = cd.get("reference") or "-"
                receive_item.user_modified = request.user.username
                receive_item.save()
                messages.success(
                    request,
                    f"Updated {receive_item.receive_item_identifier}.",
                )
            return HttpResponseRedirect(self._order_url(order, order_item))

        # Re-render with errors
        context = self.get_context_data(order=order, order_item=order_item, form=form)
        return self.render_to_response(context)
