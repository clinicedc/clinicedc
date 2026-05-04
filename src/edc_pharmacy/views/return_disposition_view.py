"""Return disposition view (central pharmacist).

After stock has been received back at central, this view lets the
central pharmacist choose a final disposition for each item:
  - repooled    → re-enters general supply
  - quarantined → set aside for investigation
  - destroyed   → removed from supply
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
from ..utils.process_return_request import disposition_return

DISPOSITION_CHOICES = [
    ("repooled", "Repooled — return to general supply"),
    ("quarantined", "Quarantined — set aside for investigation"),
    ("destroyed", "Destroyed — remove from supply"),
]


@method_decorator(login_required, name="dispatch")
class ReturnDispositionView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Central pharmacist: set final disposition on returned stock."""

    template_name = "edc_pharmacy/stock/return_disposition.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        return_request = self._get_return_request()
        # Returns that have received items needing disposition.
        pending_disposition = ReturnRequest.objects.filter(
            returnitem__stock__in_transit=False,
            returnitem__stock__dispensed=False,
            returnitem__stock__quarantined=False,
            returnitem__stock__destroyed=False,
            cancel__in=["", "N/A"],
        ).distinct().order_by("-return_datetime")

        pending_items = []
        if return_request:
            pending_items = list(
                return_request.returnitem_set.filter(
                    stock__in_transit=False,
                    stock__dispensed=False,
                    stock__quarantined=False,
                    stock__destroyed=False,
                ).select_related(
                    "stock__product__formulation",
                    "stock__allocation__registered_subject",
                )
            )

        kwargs.update(
            return_request=return_request,
            pending_disposition=pending_disposition,
            pending_items=pending_items,
            disposition_choices=DISPOSITION_CHOICES,
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
            return HttpResponseRedirect(reverse("edc_pharmacy:return_disposition_url"))

        # Each pending ReturnItem posts its disposition as disposition_<pk>.
        pending_items = return_request.returnitem_set.filter(
            stock__in_transit=False,
            stock__dispensed=False,
            stock__quarantined=False,
            stock__destroyed=False,
        ).select_related("stock")

        processed, skipped, missing = [], [], []
        for item in pending_items:
            disposition = request.POST.get(f"disposition_{item.pk}", "").strip()
            if not disposition:
                missing.append(item.stock.code)
                continue
            try:
                done, skip = disposition_return(
                    [item.stock.code], request.user, disposition=disposition
                )
                processed.extend(done)
                skipped.extend(skip)
            except ReturnError as e:
                messages.add_message(request, messages.ERROR, str(e))

        if processed:
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Dispositioned {len(processed)} item(s).",
            )
        if skipped:
            messages.add_message(
                request,
                messages.WARNING,
                f"Skipped {len(skipped)} item(s): {', '.join(skipped)}",
            )
        if missing:
            messages.add_message(
                request,
                messages.WARNING,
                f"No disposition selected for {len(missing)} item(s): {', '.join(missing)}",
            )

        pending_count = return_request.returnitem_set.filter(
            stock__in_transit=False,
            stock__dispensed=False,
            stock__quarantined=False,
            stock__destroyed=False,
        ).count()
        if pending_count > 0:
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:return_disposition_url",
                    kwargs={"return_request": return_request.pk},
                )
            )
        messages.add_message(
            request,
            messages.SUCCESS,
            f"All items dispositioned for {return_request.return_identifier}.",
        )
        return HttpResponseRedirect(reverse("edc_pharmacy:return_central_url"))
