from __future__ import annotations

import contextlib
import uuid
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_constants.constants import CONFIRMED
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import ALREADY_CONFIRMED, INVALID
from ..models import ConfirmationAtSite, Location, Stock, StockTransfer
from ..utils import confirm_stock_at_site


@method_decorator(login_required, name="dispatch")
class ConfirmationAtSiteView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/confirmation_at_site.html"
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
            locations=Location.objects.filter(
                site__in=self.request.user.userprofile.sites.all()
            ),
            location=self.location,
            location_id=self.location_id,
            stock_transfer=stock_transfer,
            stock_transfers=self.stock_transfers,
            session_uuid=str(self.session_uuid),
            CONFIRMED=CONFIRMED,
            ALREADY_CONFIRMED=ALREADY_CONFIRMED,
            INVALID=INVALID,
            **extra_opts,
        )
        return super().get_context_data(**kwargs)

    @property
    def stock_transfers(self):
        qs = StockTransfer.objects.filter(
            to_location__site=self.site,
            stocktransferitem__stock__confirmationatsiteitem__isnull=True,
        )
        return qs.annotate(count=Count("transfer_identifier")).order_by("-transfer_datetime")

    def get_adjusted_unconfirmed_count(self, stock_transfer):
        unconfirmed_count = self.get_unconfirmed_count(stock_transfer)
        return min(unconfirmed_count, 12)

    def get_stock_codes(self, stock_transfer):
        return [
            code
            for code in stock_transfer.stocktransferitem_set.values_list(
                "stock__code", flat=True
            ).all()
        ]

    def get_unconfirmed_count(self, stock_transfer) -> int:
        return (
            Stock.objects.values("code")
            .filter(
                code__in=self.get_stock_codes(stock_transfer),
                location_id=self.location_id,
                confirmationatsiteitem__isnull=True,
            )
            .count()
        )

    @property
    def site(self) -> Site | None:
        obj = None
        if self.kwargs.get("site_id"):
            with contextlib.suppress(ObjectDoesNotExist):
                obj = Site.objects.get(id=self.kwargs.get("site_id"))
        return obj

    @property
    def location_id(self) -> uuid.UUID | None:
        location_id = self.kwargs.get("location_id") or self.request.POST.get("location_id")
        if not location_id and self.site:
            try:
                location = Location.objects.get(site=self.site)
            except ObjectDoesNotExist:
                pass
            else:
                location_id = location.id
        return location_id

    @property
    def location(self) -> Location:
        try:
            location = Location.objects.get(pk=self.location_id)
        except ObjectDoesNotExist:
            location = None
        return location

    @property
    def stock_codes(self) -> list[str]:
        session_uuid = self.kwargs.get("session_uuid")
        if session_uuid:
            return self.request.session[str(session_uuid)].get("stock_codes")
        return []

    @property
    def confirmation_at_site(self):
        confirmation_at_site_id = self.kwargs.get("confirmation_at_site")
        try:
            confirmation_at_site = ConfirmationAtSite.objects.get(id=confirmation_at_site_id)
        except ObjectDoesNotExist:
            confirmation_at_site = None
            messages.add_message(
                self.request, messages.ERROR, "Invalid stock transfer confirmation."
            )
        return confirmation_at_site

    @property
    def confirmation_at_site_changelist_url(self) -> str:
        if self.confirmation_at_site:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_confirmationatsite_changelist")
            return f"{url}?q={self.confirmation_at_site.transfer_confirmation_identifier}"
        return "/"

    def get_stock_transfer(
        self,
        stock_transfer_identifier: str,
        suppress_msg: bool | None = None,
    ) -> StockTransfer | None:
        stock_transfer = None
        try:
            stock_transfer = StockTransfer.objects.get(
                transfer_identifier=stock_transfer_identifier or None,
                to_location_id=self.location_id or None,
            )
        except ObjectDoesNotExist:
            if stock_transfer_identifier and not suppress_msg:
                location = Location.objects.get(pk=self.location_id or None)
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    (
                        "Invalid Reference. Please check the manifest "
                        "reference and delivery site. "
                        f"Got {stock_transfer_identifier} at {location}."
                    ),
                )
        return stock_transfer

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:  # noqa: ARG002
        # cancel
        if request.POST.get("cancel") and request.POST.get("cancel") == "cancel":
            url = reverse("edc_pharmacy:home_url")
            return HttpResponseRedirect(url)

        stock_transfer_identifier = request.POST.get("stock_transfer_identifier")
        stock_transfer = self.get_stock_transfer(stock_transfer_identifier, suppress_msg=True)
        location_id = request.POST.get("location_id")
        if not stock_transfer or not location_id:
            # nothing selected
            url = reverse("edc_pharmacy:confirmation_at_site_url", kwargs={})
            return HttpResponseRedirect(url)

        session_uuid = request.POST.get("session_uuid")
        stock_codes = (
            request.POST.getlist("stock_codes") if request.POST.get("stock_codes") else []
        )

        # you have unconfirmed items, so go to the scan page
        if not stock_codes and stock_transfer.uncomfirmed_items > 0:
            url = reverse(
                "edc_pharmacy:confirmation_at_site_url",
                kwargs={
                    "stock_transfer_identifier": stock_transfer_identifier,
                    "location_id": location_id,
                    "items_to_scan": stock_transfer.uncomfirmed_items,
                },
            )
            return HttpResponseRedirect(url)

        if stock_codes:
            # you have scanned codes, process them
            confirmed, already_confirmed, invalid = confirm_stock_at_site(
                stock_transfer, stock_codes, location_id, request=request
            )
            # message for confirmed
            if confirmed:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Successfully confirmed {len(confirmed)} stock items. ",
                )
            # message for already confirmed
            if already_confirmed:
                messages.add_message(
                    request,
                    messages.WARNING,
                    (
                        f"Skipped {len(already_confirmed)} items. Stock items are "
                        "already confirmed."
                    ),
                )
            # message for invalid codes
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
            # return to page with any unconfirmed codes for this stock_transfer document
            # might be 0 items
            url = reverse(
                "edc_pharmacy:confirmation_at_site_url",
                kwargs={
                    "session_uuid": str(request.POST.get("session_uuid")),
                    "stock_transfer_identifier": stock_transfer_identifier,
                    "location_id": location_id,
                    "items_to_scan": stock_transfer.uncomfirmed_items,
                },
            )
            return HttpResponseRedirect(url)
        # can you get here??
        return HttpResponseRedirect(self.confirmation_at_site_changelist_url)
