"""Stock transfer workflow — create a new StockTransfer."""

from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..forms.stock import StockTransferEditForm
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class StockTransferEditView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_transfer_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, form=None, **kwargs):
        form = form or StockTransferEditForm()
        return super().get_context_data(form=form, **kwargs)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        form = StockTransferEditForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            messages.success(request, f"Stock transfer {obj.transfer_identifier} created.")
            return HttpResponseRedirect(reverse("edc_pharmacy:stock_transfer_home_url"))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
