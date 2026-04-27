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
from django.db.models import Count, F
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
        pending_returns = (
            ReturnRequest.objects.filter(
                from_location__site=self.request.site,
                cancel__in=["", "N/A"],
            )
            .annotate(dispatched_item_count=Count("returnitem"))
            .filter(dispatched_item_count__lt=F("item_count"))
            .order_by("-return_datetime")
        )

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
        # Pre-select the location that matches the current request site so
        # the pharmacist doesn't have to choose from the dropdown each time.
        try:
            current_site_location = Location.objects.get(site=self.request.site)
        except (Location.DoesNotExist, Location.MultipleObjectsReturned):
            current_site_location = None

        kwargs.update(
            return_request=return_request,
            pending_returns=pending_returns,
            dispatched_count=dispatched_count,
            remaining_count=remaining_count,
            item_count=list(range(1, items_to_scan + 1)),
            central_location=central_location,
            from_locations=from_locations,
            current_site_location=current_site_location,
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

        # --- Phase 1a: delete an empty ReturnRequest ---
        if not return_request and request.POST.get("delete_pk"):
            try:
                rr = ReturnRequest.objects.get(pk=request.POST["delete_pk"])
                if rr.returnitem_set.exists():
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Cannot delete {rr.return_identifier}: items already dispatched.",
                    )
                else:
                    identifier = rr.return_identifier
                    rr.delete()
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Return request {identifier} deleted.",
                    )
            except ReturnRequest.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Return request not found.")
            return HttpResponseRedirect(reverse("edc_pharmacy:return_request_url"))

        # --- Phase 1b: create a new ReturnRequest and flag codes ---
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

        # --- Phase 2a: update the expected item count ---
        if request.POST.get("update_item_count"):
            try:
                new_count = int(request.POST.get("item_count", 0))
                dispatched_count = return_request.returnitem_set.count()
                if new_count < dispatched_count:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Cannot set count to {new_count}: "
                        f"{dispatched_count} item(s) already dispatched.",
                    )
                else:
                    return_request.item_count = new_count
                    return_request.save(update_fields=["item_count"])
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Expected count updated to {new_count}.",
                    )
            except (ValueError, TypeError):
                messages.add_message(request, messages.ERROR, "Invalid item count.")
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:return_request_url",
                    kwargs={"return_request": return_request.pk},
                )
            )

        # --- Phase 2b: dispatch stock codes on an existing ReturnRequest ---
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
        if dispatched_count >= (return_request.item_count or 0):
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Return request {return_request.return_identifier} complete: "
                f"{dispatched_count} item(s) dispatched to central.",
            )
            return HttpResponseRedirect(reverse("edc_pharmacy:return_request_url"))
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:return_request_url",
                kwargs={"return_request": return_request.pk},
            )
        )
