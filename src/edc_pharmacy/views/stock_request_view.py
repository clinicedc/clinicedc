"""Stock request workflow — per-request page with Prepare / Allocate / Cancel actions."""

from __future__ import annotations

from clinicedc_constants import CANCEL
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
from ..models import Allocation, StockRequest
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class StockRequestView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_request_manage.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def _get_stock_request(self) -> StockRequest:
        return get_object_or_404(StockRequest, pk=self.kwargs["stock_request"])

    def get_context_data(self, **kwargs):
        kwargs.pop("stock_request", None)
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        sr = self._get_stock_request()
        total = sr.stockrequestitem_set.count()
        allocated = sr.stockrequestitem_set.filter(allocation__isnull=False).count()
        pending = total - allocated
        allocations = (
            Allocation.objects.filter(stock_request_item__stock_request=sr)
            .select_related("registered_subject", "assignment")
            .order_by("allocation_datetime")
        )
        context.update(
            stock_request=sr,
            total=total,
            allocated=allocated,
            pending=pending,
            allocations=allocations,
            show_assignment=PHARMACIST_ROLE in roles,
        )
        return context

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        sr = self._get_stock_request()
        redirect_url = reverse(
            "edc_pharmacy:stock_request_url", kwargs={"stock_request": sr.pk}
        )
        action = request.POST.get("action")
        if action == "cancel":
            return self._handle_cancel(request, sr, redirect_url)
        return HttpResponseRedirect(redirect_url)

    @staticmethod
    def _handle_cancel(
        request, sr: StockRequest, redirect_url: str
    ) -> HttpResponseRedirect:
        if Allocation.objects.filter(stock_request_item__stock_request=sr).exists():
            messages.error(
                request,
                "Cannot cancel — stock has already been allocated for this request.",
            )
            return HttpResponseRedirect(redirect_url)
        sr.cancel = CANCEL
        sr.user_modified = request.user.username
        sr.save()
        messages.success(request, f"Stock request {sr.request_identifier} cancelled.")
        return HttpResponseRedirect(
            reverse("edc_pharmacy:stock_request_home_url")
        )
