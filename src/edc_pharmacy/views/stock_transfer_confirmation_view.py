from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Location, Stock, StockTransferConfirmation
from ..utils import confirm_stock_at_site


@method_decorator(login_required, name="dispatch")
class StockTransferConfirmationView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/stock_transfer_confirmation.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        session_uuid = self.kwargs.get("session_uuid")
        last_codes = []
        if session_uuid:
            session_obj = self.request.session[str(session_uuid)]
            last_codes = [(x, "confirmed") for x in session_obj.get("confirmed") or []]
            last_codes.extend(
                [(x, "already confirmed") for x in session_obj.get("already_confirmed") or []]
            )
            last_codes.extend([(x, "invalid") for x in session_obj.get("invalid") or []])
        unconfirmed_count = (
            Stock.objects.values("pk")
            .filter(pk__in=self.stock_pks, location=self.location, confirmed=False)
            .count()
        )
        unconfirmed_count = 12 if unconfirmed_count > 12 else unconfirmed_count
        kwargs.update(
            locations=Location.objects.filter(site__isnull=False),
            location=self.location,
            item_count=list(range(1, unconfirmed_count + 1)),
            unconfirmed_count=unconfirmed_count,
            # source_changelist_url=self.source_changelist_url,
            last_codes=last_codes,
        )
        return super().get_context_data(**kwargs)

    @property
    def location(self) -> Location:
        location = None
        if location_id := self.kwargs.get("location_id"):
            location = Location.objects.get(pk=location_id)
        return location

    @property
    def stock_pks(self):
        session_uuid = self.kwargs.get("session_uuid")
        return self.request.session[str(session_uuid)].get("queryset")

    @property
    def stock_transfer_confirmation(self):
        stock_transfer_confirmation_id = self.kwargs.get("stock_transfer_confirmation")
        try:
            stock_transfer_confirmation = StockTransferConfirmation.objects.get(
                id=stock_transfer_confirmation_id
            )
        except ObjectDoesNotExist:
            stock_transfer_confirmation = None
            messages.add_message(
                self.request, messages.ERROR, "Invalid stock transfer confirmation."
            )
        return stock_transfer_confirmation

    @property
    @property
    def stock_transfer_confirmation_changelist_url(self) -> str:
        if self.stock_transfer_confirmation:
            url = reverse(
                "edc_pharmacy_admin:edc_pharmacy_stocktransferconfirmation_changelist"
            )
            url = (
                f"{url}?q={self.stock_transfer_confirmation.transfer_confirmation_identifier}"
            )
            return url
        return "/"

    def post(self, request, *args, **kwargs):
        stock_codes = request.POST.getlist("codes") if request.POST.get("codes") else []
        location_id = request.POST.get("location_id")
        items_to_scan = int(request.POST.get("items_to_scan") or 0) - len(stock_codes)
        if not stock_codes and location_id and items_to_scan > 0:
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={
                    "location_id": location_id,
                    "items_to_scan": items_to_scan,
                },
            )
            return HttpResponseRedirect(url)

        elif stock_codes and location_id:
            confirmed, already_confirmed, invalid = confirm_stock_at_site(
                stock_codes, location_id, request.user.username
            )
            if confirmed:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Successfully confirmed {len(confirmed)} stock items. ",
                )
            if already_confirmed:
                messages.add_message(
                    request,
                    messages.WARNING,
                    (
                        f"Skipped {len(already_confirmed)} items. Stock items are "
                        "already confirmed."
                    ),
                )
            if invalid:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Invalid codes submitted! Got {', '.join(invalid)} .",
                )
            self.request.session[str(self.kwargs.get("session_uuid"))] = dict(
                confirmed=confirmed,
                already_confirmed=already_confirmed,
                invalid=invalid,
            )
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={"location_id": location_id, "items_to_scan": items_to_scan},
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.stock_transfer_confirmation_changelist_url)
