"""Order management — add or edit a single OrderItem."""

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

from ..forms.stock import OrderItemAddForm
from ..models import Order, OrderItem
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class OrderItemEditView(
    AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/order_item_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    def get_order_item(self, order):
        order_item_pk = self.kwargs.get("order_item")
        if order_item_pk:
            return get_object_or_404(OrderItem, pk=order_item_pk, order=order)
        return None

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("order", None)
        kwargs.pop("order_item", None)
        context = super().get_context_data(**kwargs)
        order = self.get_order()
        order_item = self.get_order_item(order)
        if form is None:
            form = OrderItemAddForm(instance=order_item, order=order)
        context.update(order=order, order_item=order_item, form=form)
        return context

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        order = self.get_order()
        order_item = self.get_order_item(order)
        form = OrderItemAddForm(request.POST, instance=order_item, order=order)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.order = order
            if not obj.id:
                obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            verb = "added" if order_item is None else "updated"
            messages.success(
                request,
                f"Order item {obj.order_item_identifier} {verb}.",
            )
            return HttpResponseRedirect(
                reverse("edc_pharmacy:order_url", kwargs={"order": order.pk})
            )
        return self.render_to_response(self.get_context_data(form=form))
