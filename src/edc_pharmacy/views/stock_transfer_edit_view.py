"""Stock transfer workflow — create or edit a StockTransfer header.

Modes:
  - Create: ``/stock-transfer/add/`` (no URL kwarg). Saves and redirects to
    the home page.
  - Edit:   ``/stock-transfer/<uuid>/edit/`` (uuid kwarg). Saves and
    redirects back to the transfer-stock page.
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

from ..forms.stock import StockTransferEditForm
from ..models import StockTransfer
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class StockTransferEditView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_transfer_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_stock_transfer(self):
        pk = self.kwargs.get("stock_transfer")
        if pk:
            return get_object_or_404(StockTransfer, pk=pk)
        return None

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("stock_transfer", None)
        stock_transfer = self.get_stock_transfer()
        form = form or StockTransferEditForm(instance=stock_transfer)
        return super().get_context_data(
            form=form, stock_transfer=stock_transfer, **kwargs
        )

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        stock_transfer = self.get_stock_transfer()
        form = StockTransferEditForm(request.POST, instance=stock_transfer)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.id:
                obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            verb = "updated" if stock_transfer else "created"
            messages.success(
                request, f"Stock transfer {obj.transfer_identifier} {verb}."
            )
            if stock_transfer:
                return HttpResponseRedirect(
                    reverse(
                        "edc_pharmacy:transfer_stock_url",
                        kwargs={"stock_transfer": obj.pk},
                    )
                )
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_transfer_home_url"))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
