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

from ..models import Location, StockTransferConfirmation
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
        kwargs.update(
            # stock_transfer_confirmation=self.stock_transfer_confirmation,
            item_count=list(range(1, 13)),
            locations=Location.objects.filter(site__isnull=False),
            location=self.location,
        )
        return super().get_context_data(**kwargs)

    @property
    def location(self) -> Location:
        location = None
        if location_id := self.kwargs.get("location_id"):
            location = Location.objects.get(pk=location_id)
        return location

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
        stock_codes = request.POST.getlist("codes") if request.POST.get("codes") else None
        location_id = request.POST.get("location_id")
        if not stock_codes and location_id:
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={"location_id": location_id},
            )
            return HttpResponseRedirect(url)

        elif stock_codes and location_id:
            confirmed, not_confirmed = confirm_stock_at_site(
                stock_codes, location_id, request.user.username
            )
            messages.add_message(
                self.request,
                messages.SUCCESS,
                f"Confirmed {confirmed} item.",
            )
            if not_confirmed:
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    f"{not_confirmed} items were skipped.",
                )

            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={"location_id": location_id},
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.stock_transfer_confirmation_changelist_url)
