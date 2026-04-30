"""Receive workflow — dedicated page for editing the Receive header.

Mirrors the order-edit page (clean form, nothing else on the page) so the
[Edit] button on the Receive record panel doesn't expand into the panel
alongside read-only data.

URL:  /receive/<order>/header/edit/   name: receive_edit_url
On save: redirect back to the per-order receive page.
On cancel: same.

Creation of a Receive record is still handled inline by ReceiveOrderView
(when no Receive record exists), via action=save_receive POST.
"""

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

from ..forms.stock import ReceiveHeaderForm
from ..models import Order, Receive
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class ReceiveEditView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/receive_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    @staticmethod
    def get_receive(order):
        try:
            return Receive.objects.get(order=order)
        except Receive.DoesNotExist:
            return None

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("order", None)
        order = self.get_order()
        receive = self.get_receive(order)
        form = form or ReceiveHeaderForm(instance=receive)
        return super().get_context_data(
            order=order, receive=receive, form=form, **kwargs
        )

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        order = self.get_order()
        receive = self.get_receive(order)
        if receive is None:
            messages.error(
                request, "No receive record exists yet. Create one first."
            )
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        form = ReceiveHeaderForm(request.POST, instance=receive)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.order = order
            obj.supplier = order.supplier
            # User supplies the date; server appends the current time.
            receive_date = form.cleaned_data["receive_date"]
            now = timezone.localtime(timezone.now())
            obj.receive_datetime = now.replace(
                year=receive_date.year,
                month=receive_date.month,
                day=receive_date.day,
                microsecond=0,
            )
            obj.user_modified = request.user.username
            obj.save()
            messages.success(
                request, f"Receive record {obj.receive_identifier} updated."
            )
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        return self.render_to_response(self.get_context_data(form=form))
