"""Return receive view (central pharmacist).

Central confirms receipt of stock returned from a site.
Scans codes and calls receive_return() for each.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..exceptions import ReturnError
from ..models import ReturnRequest
from ..utils.process_return_request import receive_return


@method_decorator(login_required, name="dispatch")
class ReturnReceiveView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Central pharmacist: confirm receipt of returned stock."""

    template_name = "edc_pharmacy/stock/return_receive.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        return_request = self._get_return_request()
        pending_receipts = ReturnRequest.objects.filter(
            returnitem__stock__in_transit=True,
            cancel__in=["", "N/A"],
        ).distinct().order_by("-return_datetime")

        received_count = 0
        pending_count = 0
        if return_request:
            received_count = return_request.returnitem_set.filter(
                stock__in_transit=False,
                stock__confirmed_at_location=False,
            ).count()
            pending_count = return_request.returnitem_set.filter(
                stock__in_transit=True,
            ).count()
            items_to_scan = min(pending_count, 12)
        else:
            items_to_scan = 0

        kwargs.update(
            return_request=return_request,
            pending_receipts=pending_receipts,
            received_count=received_count,
            pending_count=pending_count,
            item_count=list(range(1, items_to_scan + 1)),
            changelist_url=reverse(
                "edc_pharmacy_admin:edc_pharmacy_returnrequest_changelist"
            ),
        )
        return super().get_context_data(**kwargs)

    def _get_return_request(self) -> ReturnRequest | None:
        pk = self.kwargs.get("return_request")
        if pk:
            try:
                return ReturnRequest.objects.get(pk=pk)
            except ObjectDoesNotExist:
                messages.add_message(
                    self.request, messages.ERROR, "Return request not found."
                )
        return None

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        return_request = self._get_return_request()
        if not return_request:
            return HttpResponseRedirect(reverse("edc_pharmacy:return_receive_url"))

        stock_codes = [c.strip().upper() for c in request.POST.getlist("codes") if c.strip()]
        if stock_codes:
            try:
                received, skipped = receive_return(
                    return_request, stock_codes, request.user
                )
            except ReturnError as e:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                if received:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Received {len(received)} item(s).",
                    )
                if skipped:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        f"Skipped {len(skipped)} item(s): {', '.join(skipped)}",
                    )

        pending_count = return_request.returnitem_set.filter(
            stock__in_transit=True
        ).count()
        if pending_count > 0:
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:return_receive_url",
                    kwargs={"return_request": return_request.pk},
                )
            )
        return HttpResponseRedirect(
            reverse("edc_pharmacy_admin:edc_pharmacy_returnrequest_changelist")
        )
