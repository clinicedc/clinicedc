"""Combined returns view for the central pharmacist.

Shows two panels on one page:
  1. Receive Returned Stock  — in-transit returns awaiting receipt confirmation.
  2. Return Disposition      — received returns awaiting final disposition.

Phase 2 scanning for each action is handled by the existing per-UUID views
(ReturnReceiveView and ReturnDispositionView), which redirect back here on
completion.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import ReturnRequest


@method_decorator(login_required, name="dispatch")
class ReturnCentralView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Central pharmacist: combined receive + disposition dashboard."""

    template_name = "edc_pharmacy/stock/return_central.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        pending_receipts = (
            ReturnRequest.objects.filter(
                returnitem__stock__in_transit=True,
                cancel__in=["", "N/A"],
            )
            .distinct()
            .order_by("-return_datetime")
        )
        pending_disposition = (
            ReturnRequest.objects.filter(
                returnitem__stock__in_transit=False,
                returnitem__stock__dispensed=False,
                returnitem__stock__quarantined=False,
                returnitem__stock__destroyed=False,
                cancel__in=["", "N/A"],
            )
            .distinct()
            .order_by("-return_datetime")
        )
        kwargs.update(
            pending_receipts=pending_receipts,
            pending_disposition=pending_disposition,
        )
        return super().get_context_data(**kwargs)
