"""Stock request workflow — landing page."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..models import StockRequest
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class StockRequestHomeView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_request_home.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        show_assignment = PHARMACIST_ROLE in roles
        requests = StockRequest.objects.select_related(
            "location", "formulation", "container",
        ).order_by("-request_identifier")
        rows = []
        for sr in requests:
            total = sr.stockrequestitem_set.count()
            allocated = sr.stockrequestitem_set.filter(allocation__isnull=False).count()
            rows.append({"sr": sr, "total": total, "allocated": allocated})
        context["rows"] = rows
        context["show_assignment"] = show_assignment
        return context
