"""Receive workflow — order edit page."""

from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..forms.stock import OrderEditForm
from ..models import Order


@method_decorator(login_required, name="dispatch")
class ReceiveOrderEditView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    template_name = "edc_pharmacy/stock/receive_order_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("order", None)
        order = self.get_order()
        form = form or OrderEditForm(instance=order)
        return super().get_context_data(order=order, form=form, **kwargs)

    def post(self, request, *args, **kwargs):
        order = self.get_order()
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            obj = form.save(commit=False)
            order_date = form.cleaned_data["order_date"]
            now = timezone.localtime(timezone.now())
            obj.order_datetime = now.replace(
                year=order_date.year,
                month=order_date.month,
                day=order_date.day,
                microsecond=0,
            )
            obj.user_modified = request.user.username
            obj.save()
            messages.success(request, f"Order {obj.order_identifier} updated.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
