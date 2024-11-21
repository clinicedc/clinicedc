from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_constants.constants import CONFIRMED
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import ALREADY_CONFIRMED, INVALID
from ..models import Location, Stock, StockTransfer, StockTransferConfirmation
from ..utils import confirm_stock_at_site


@method_decorator(login_required, name="dispatch")
class StockTransferConfirmationView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/stock_transfer_confirmation.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def __init__(self, **kwargs):
        self.session_uuid: str | None = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        extra_opts = {}
        stock_transfer = self.get_stock_transfer(self.kwargs.get("stock_transfer_identifier"))
        if not self.kwargs.get("session_uuid"):
            self.session_uuid = str(uuid4())
            session_obj = None
        else:
            self.session_uuid = str(self.kwargs.get("session_uuid"))
            session_obj = self.request.session[self.session_uuid]
        if stock_transfer:
            unconfirmed_count = self.get_unconfirmed_count(stock_transfer)
            extra_opts = dict(
                unconfirmed_count=unconfirmed_count,
                item_count=list(
                    range(1, self.get_adjusted_unconfirmed_count(stock_transfer) + 1)
                ),
                last_codes=[],
            )
        if session_obj:
            last_codes = [(x, "confirmed") for x in session_obj.get("confirmed") or []]
            last_codes.extend(
                [(x, "already confirmed") for x in session_obj.get("already_confirmed") or []]
            )
            last_codes.extend([(x, "invalid") for x in session_obj.get("invalid") or []])
            unconfirmed_count = self.get_unconfirmed_count(stock_transfer)
            extra_opts.update(
                item_count=list(
                    range(1, self.get_adjusted_unconfirmed_count(stock_transfer) + 1)
                ),
                unconfirmed_count=unconfirmed_count,
                last_codes=last_codes,
            )
        kwargs.update(
            locations=Location.objects.filter(site__isnull=False),
            location=self.location,
            stock_transfer=stock_transfer,
            session_uuid=str(self.session_uuid),
            CONFIRMED=CONFIRMED,
            ALREADY_CONFIRMED=ALREADY_CONFIRMED,
            INVALID=INVALID,
            **extra_opts,
        )
        return super().get_context_data(**kwargs)

    def get_adjusted_unconfirmed_count(self, stock_transfer):
        unconfirmed_count = self.get_unconfirmed_count(stock_transfer)
        return 12 if unconfirmed_count > 12 else unconfirmed_count

    def get_stock_codes(self, stock_transfer):
        stock_codes = [
            code
            for code in stock_transfer.stocktransferitem_set.values_list(
                "stock__code", flat=True
            ).all()
        ]
        return stock_codes

    def get_unconfirmed_count(self, stock_transfer) -> int:
        return (
            Stock.objects.values("code")
            .filter(
                code__in=self.get_stock_codes(stock_transfer),
                location=self.location,
                confirmed_at_site=False,
            )
            .count()
        )

    @property
    def location(self) -> Location:
        location = None
        if location_id := self.kwargs.get("location_id"):
            location = Location.objects.get(pk=location_id)
        return location

    @property
    def stock_codes(self) -> list[str]:
        session_uuid = self.kwargs.get("session_uuid")
        if session_uuid:
            return self.request.session[str(session_uuid)].get("stock_codes")
        return []

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

    def get_stock_transfer(
        self, stock_transfer_identifier: str, suppress_msg: bool = None
    ) -> StockTransfer | None:
        stock_transfer = None
        try:
            stock_transfer = StockTransfer.objects.get(
                transfer_identifier=stock_transfer_identifier,
                to_location=self.location,
            )
        except ObjectDoesNotExist:
            if stock_transfer_identifier and not suppress_msg:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    (
                        "Invalid Reference. Please check the manifest "
                        "reference and delivery site. "
                        f"Got {stock_transfer_identifier} at {self.location}."
                    ),
                )
        return stock_transfer

    def post(self, request, *args, **kwargs):

        stock_transfer_identifier = request.POST.get("stock_transfer_identifier")
        session_uuid = request.POST.get("session_uuid")
        location_id = request.POST.get("location_id")
        items_to_scan = int(request.POST.get("items_to_scan") or 0)
        stock_transfer = self.get_stock_transfer(stock_transfer_identifier, suppress_msg=True)
        if not stock_transfer:
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={
                    "stock_transfer_identifier": stock_transfer_identifier,
                    "location_id": location_id,
                    "items_to_scan": items_to_scan,
                },
            )
            return HttpResponseRedirect(url)

        stock_codes = (
            request.POST.getlist("stock_codes") if request.POST.get("stock_codes") else []
        )
        items_to_scan = int(request.POST.get("items_to_scan") or 0) - len(
            list(set(stock_codes))
        )

        if not stock_codes and location_id and items_to_scan > 0:
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={
                    "stock_transfer_identifier": stock_transfer_identifier,
                    "location_id": location_id,
                    "items_to_scan": 0 if items_to_scan < 0 else items_to_scan,
                },
            )
            return HttpResponseRedirect(url)

        elif stock_codes and location_id:
            confirmed, already_confirmed, invalid = confirm_stock_at_site(
                stock_transfer, stock_codes, location_id, request.user.username
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
            self.request.session[session_uuid] = dict(
                confirmed=confirmed,
                already_confirmed=already_confirmed,
                invalid=invalid,
                stock_transfer_pk=str(stock_transfer.pk),
            )
            url = reverse(
                "edc_pharmacy:stock_transfer_confirmation_url",
                kwargs={
                    "session_uuid": str(request.POST.get("session_uuid")),
                    "stock_transfer_identifier": stock_transfer_identifier,
                    "location_id": location_id,
                    "items_to_scan": 0 if items_to_scan < 0 else items_to_scan,
                },
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.stock_transfer_confirmation_changelist_url)
