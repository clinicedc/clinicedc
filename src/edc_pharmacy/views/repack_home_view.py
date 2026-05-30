"""Repack workflow — landing page."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..models import RepackRequest, Stock
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class RepackHomeView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/repack_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        show_assignment = PHARMACIST_ROLE in roles
        repack_requests = RepackRequest.objects.select_related(
            "from_stock__product", "from_stock__product__assignment",
            "from_stock__lot", "container",
        ).order_by("-repack_identifier")
        confirmed_map = {
            rr.pk: Stock.objects.filter(repack_request=rr, confirmed=True).count()
            for rr in repack_requests
        }
        rows = [
            {
                "rr": rr,
                "confirmed_qty": confirmed_map.get(rr.pk, 0),
            }
            for rr in repack_requests
        ]
        context["rows"] = rows
        context["show_assignment"] = show_assignment
        return context
