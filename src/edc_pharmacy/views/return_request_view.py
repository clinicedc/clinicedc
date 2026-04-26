"""Return request / dispatch view (site pharmacist).

Two phases on the same URL:

  Phase 1 — no return_request kwarg:
    POST with stock_codes → calls request_stock_return() to flag each code
    as return_requested, then redirects back with the return_request pk
    that was created (or a fresh one is created).

  Phase 2 — return_request kwarg present:
    POST with codes → calls dispatch_return() to mark each code as
    in_transit to central and creates ReturnItem rows.
"""

from __future__ import annotations

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import CENTRAL_LOCATION
from ..exceptions import ReturnError
from ..models import Location, ReturnRequest
from ..utils.process_return_request import dispatch_return, request_stock_return


@method_decorator(login_required, name="dispatch")
class ReturnRequestView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Site pharmacist: request and dispatch stock returns to central."""

    template_name = "edc_pharmacy/stock/return_request.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        return_request = self._get_return_request()
        pending_returns = ReturnRequest.objects.filter(
            from_location__site=self.request.site,
            cancel__in=["", "N/A"],
        ).order_by("-return_datetime")

        dispatched_count = 0
        remaining_count = 0
        if return_request:
            dispatched_count = return_request.returnitem_set.count()
            remaining_count = max(
                0, (return_request.item_count or 0) - dispatched_count
            )
            items_to_scan = min(remaining_count, 12)
        else:
            items_to_scan = 0

        try:
            central_location = Location.objects.get(name=CENTRAL_LOCATION)
        except Location.DoesNotExist:
            central_location = None

        from_locations = Location.objects.filter(
            site__in=self.request.user.userprofile.sites.all()
        )

        kwargs.update(
            return_request=return_request,
            pending_returns=pending_returns,
            dispatched_count=dispatched_count,
            remaining_count=remaining_count,
            item_count=list(range(1, items_to_scan + 1)),
            central_location=central_location,
            from_locations=from_locations,
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
            except ReturnRequest.DoesNotExist:
                messages.add_message(
                    self.request, messages.ERROR, "Return request not found."
                )
        return None

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        return_request = self._get_return_request()

        # --- Phase 1: create a new ReturnRequest and flag codes ---
        if not return_request:
            from_location_id = request.POST.get("from_location_id")
            item_count = request.POST.get("item_count")
            comment = request.POST.get("comment", "")
            try:
                from_location = Location.objects.get(pk=from_location_id)
                central_location = Location.objects.get(name=CENTRAL_LOCATION)
            except Location.DoesNotExist as e:
                messages.add_message(request, messages.ERROR, str(e))
                return HttpResponseRedirect(reverse("edc_pharmacy:return_request_url"))

            try:
                return_request = ReturnRequest.objects.create(
                    from_location=from_location,
                    to_location=central_location,
                    item_count=int(item_count or 0),
                    comment=comment,
                    return_datetime=timezone.now(),
                    user_created=request.user.username,
                )
            except (ReturnError, ValueError) as e:
                messages.add_message(request, messages.ERROR, str(e))
                return HttpResponseRedirect(reverse("edc_pharmacy:return_request_url"))

            messages.add_message(
                request,
                messages.SUCCESS,
                f"Return request {return_request.return_identifier} created.",
            )
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:return_request_url",
                    kwargs={"return_request": return_request.pk},
                )
            )

        # --- Phase 2: dispatch stock codes on an existing ReturnRequest ---
        stock_codes = [c.strip().upper() for c in request.POST.getlist("codes") if c.strip()]
        if stock_codes:
            try:
                dispatched, skipped = dispatch_return(
                    return_request, stock_codes, request.user
                )
            except ReturnError as e:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                if dispatched:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Dispatched {len(dispatched)} item(s).",
                    )
                if skipped:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        f"Skipped {len(skipped)} item(s): {', '.join(skipped)}",
                    )

        dispatched_count = return_request.returnitem_set.count()
        if dispatched_count < (return_request.item_count or 0):
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:return_request_url",
                    kwargs={"return_request": return_request.pk},
                )
            )
        return HttpResponseRedirect(
            reverse("edc_pharmacy_admin:edc_pharmacy_returnrequest_changelist")
        )
