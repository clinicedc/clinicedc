from __future__ import annotations

import contextlib
import uuid
from uuid import uuid4

from clinicedc_constants import CONFIRMED
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

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import ALREADY_CONFIRMED, CENTRAL_LOCATION, INVALID
from ..forms.stock import SCAN_GRID_PAGE_SIZE, ConfirmAtLocationEntryForm
from ..models import ConfirmationAtLocation, Location, StockTransfer
from ..utils import confirm_stock_at_location


@method_decorator(login_required, name="dispatch")
class ConfirmaAtLocationView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/confirm_at_location.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def __init__(self, **kwargs):
        self.session_uuid: str | None = None
        super().__init__(**kwargs)

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        extra_opts: dict = {}
        stock_transfer = self.get_stock_transfer(self.kwargs.get("stock_transfer_identifier"))

        if not self.kwargs.get("session_uuid"):
            self.session_uuid = str(uuid4())
            session_obj = None
        else:
            self.session_uuid = str(self.kwargs.get("session_uuid"))
            session_obj = self.request.session[self.session_uuid]

        if stock_transfer:
            # On the scan page, ``items_to_scan`` (URL kwarg) is the
            # number of physical bottles the user still has to scan in
            # this workflow. The grid renders min(items_to_scan,
            # SCAN_GRID_PAGE_SIZE) rows; after submit the view decrements
            # items_to_scan and redirects until it reaches 0.
            items_to_scan = self.kwargs.get("items_to_scan")
            try:
                items_to_scan = int(items_to_scan) if items_to_scan else 0
            except (TypeError, ValueError):
                items_to_scan = 0
            items_to_scan = max(items_to_scan, 0)
            grid_size = min(items_to_scan, SCAN_GRID_PAGE_SIZE)
            extra_opts = dict(
                unconfirmed_count=stock_transfer.unconfirmed_items,
                items_to_scan=items_to_scan,
                grid_size=grid_size,
                item_count=list(range(1, grid_size + 1)),
                last_codes=[],
            )

        if session_obj:
            # last_codes is stored in SCAN ORDER (the order the pharmacist
            # filled the input grid), tagged with bucket label. Built in
            # _handle_scan_submission below.
            extra_opts.update(
                last_codes=session_obj.get("last_codes") or [],
                last_scanned_count=session_obj.get("last_scanned_count") or 0,
            )

        location_qs = self._location_queryset()

        # Entry form lives on the initial page only (no stock_transfer in
        # context). Once the user is on the scan page we don't need it.
        entry_form = kwargs.pop("entry_form", None)
        if entry_form is None and not stock_transfer:
            entry_form = ConfirmAtLocationEntryForm(location_queryset=location_qs)

        # When the entry form is being re-rendered after a validation
        # failure, the user already chose a Location and a Reference. The
        # Reference <select> is normally populated by JS via the
        # get-stock-transfers endpoint on Location change — but that JS
        # hasn't fired on form redisplay, so we'd lose the options. Pre-
        # render them server-side based on the bound Location.
        prefilled_transfers = self._prefilled_transfers(entry_form)

        kwargs.update(
            entry_form=entry_form,
            prefilled_transfers=prefilled_transfers,
            locations=location_qs,
            location=self.location,
            location_id=self.location_id,
            stock_transfer=stock_transfer,
            stock_transfers=self.stock_transfers,
            session_uuid=str(self.session_uuid),
            SCAN_GRID_PAGE_SIZE=SCAN_GRID_PAGE_SIZE,
            CONFIRMED=CONFIRMED,
            ALREADY_CONFIRMED=ALREADY_CONFIRMED,
            INVALID=INVALID,
            **extra_opts,
        )
        return super().get_context_data(**kwargs)

    def _prefilled_transfers(self, entry_form) -> list[dict]:
        """Return server-side data for the Reference <select> on
        validation-error redisplay. Mirrors the JSON shape produced by
        ``get_stock_transfers_view`` so the JS can read it identically.
        """
        if entry_form is None or not entry_form.is_bound:
            return []
        # Use raw data (not cleaned_data) — cleaned_data may be missing
        # if the bound location failed its own validation.
        raw_location_id = entry_form.data.get("location") or None
        if not raw_location_id:
            return []
        transfers = (
            StockTransfer.objects.filter(
                to_location_id=raw_location_id,
                stocktransferitem__confirmationatlocationitem__isnull=True,
            )
            .distinct()
            .order_by("-transfer_identifier")
        )
        return [
            {
                "transfer_identifier": t.transfer_identifier,
                "item_count": t.item_count,
                "unconfirmed_items": t.unconfirmed_items,
            }
            for t in transfers
        ]

    # ------------------------------------------------------------------
    # Queryset helpers
    # ------------------------------------------------------------------
    def _location_queryset(self):
        if self.kwargs.get("location_name") == CENTRAL_LOCATION:
            return Location.objects.filter(name=CENTRAL_LOCATION)
        return Location.objects.filter(
            site__in=self.request.user.userprofile.sites.all()
        )

    @property
    def stock_transfers(self):
        qs = StockTransfer.objects.filter(
            to_location__site=self.site,
            stocktransferitem__confirmationatlocationitem__isnull=True,
        )
        return qs.annotate(count=Count("transfer_identifier")).order_by("-transfer_datetime")

    def get_stock_codes(self, stock_transfer):
        return [
            code
            for code in stock_transfer.stocktransferitem_set.values_list(
                "stock__code", flat=True
            ).all()
        ]

    def get_unconfirmed_count(self, stock_transfer) -> int:
        return stock_transfer.stocktransferitem_set.filter(
            confirmationatlocationitem__isnull=True
        ).count()

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
    def confirm_at_location(self):
        confirm_at_location_id = self.kwargs.get("confirm_at_location")
        try:
            confirm_at_location = ConfirmationAtLocation.objects.get(id=confirm_at_location_id)
        except ObjectDoesNotExist:
            confirm_at_location = None
            messages.add_message(
                self.request, messages.ERROR, "Invalid stock transfer confirmation."
            )
        return confirm_at_location

    @property
    def confirm_at_location_changelist_url(self) -> str:
        if self.confirm_at_location:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_confirmationatlocation_changelist")
            return f"{url}?q={self.confirm_at_location.transfer_confirmation_identifier}"
        return "/"

    def get_stock_transfer(
        self,
        stock_transfer_identifier: str,
        suppress_msg: bool | None = None,
    ) -> StockTransfer | None:
        """Lookup helper used only for the scan-page context.

        The entry form has its own validation; this helper is for URLs
        that already carry a stock_transfer_identifier kwarg (i.e. we're
        on the scan page already) and just need to look it up.
        """
        stock_transfer = None
        if stock_transfer_identifier is None:
            return None
        try:
            stock_transfer = StockTransfer.objects.get(
                transfer_identifier=stock_transfer_identifier or None,
                to_location_id=self.location_id or None,
            )
        except ObjectDoesNotExist:
            if not suppress_msg:
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

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------
    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:  # noqa: ARG002
        # Cancel goes home.
        if request.POST.get("cancel") == "cancel":
            return HttpResponseRedirect(reverse("edc_pharmacy:home_url"))

        # If scanned codes are present, this is a scan-page submission.
        # Process them and redirect back to the scan page.
        if request.POST.getlist("stock_codes"):
            return self._handle_scan_submission(request)

        # Otherwise treat this as the entry-form submission.
        return self._handle_entry_submission(request)

    def _handle_entry_submission(self, request) -> HttpResponseRedirect:
        location_qs = self._location_queryset()
        form = ConfirmAtLocationEntryForm(request.POST, location_queryset=location_qs)
        if not form.is_valid():
            # Re-render the entry page with the bound form (errors and all).
            context = self.get_context_data(entry_form=form)
            return self.render_to_response(context)

        stock_transfer = form.cleaned_data["stock_transfer"]
        number_of_items = form.cleaned_data["number_of_items"]
        url = reverse(
            "edc_pharmacy:confirm_at_location_url",
            kwargs={
                "stock_transfer_identifier": stock_transfer.transfer_identifier,
                "location_id": form.cleaned_data["location"].id,
                "items_to_scan": number_of_items,
            },
        )
        return HttpResponseRedirect(url)

    def _handle_scan_submission(self, request) -> HttpResponseRedirect:
        stock_transfer_identifier = request.POST.get("stock_transfer_identifier")
        stock_transfer = self.get_stock_transfer(stock_transfer_identifier, suppress_msg=True)
        location_id = request.POST.get("location_id")
        if not stock_transfer or not location_id:
            return HttpResponseRedirect(reverse("edc_pharmacy:confirm_at_location_url"))

        session_uuid = request.POST.get("session_uuid")
        stock_codes = request.POST.getlist("stock_codes")

        # Carry through the user's intended total for the multi-page scan
        # workflow. Decrement by the number of inputs the user submitted
        # this page — every physical bottle they scanned counts toward
        # their target, regardless of confirmation outcome (already-
        # confirmed and invalid bottles still passed through their hands).
        try:
            prev_items_to_scan = int(request.POST.get("items_to_scan") or 0)
        except (TypeError, ValueError):
            prev_items_to_scan = 0

        confirmed, already_confirmed, invalid = confirm_stock_at_location(
            stock_transfer, stock_codes, location_id, request=request
        )

        # Build last_codes in scan order — the order codes appeared in
        # request.POST.getlist("stock_codes") is the order the pharmacist
        # filled the input grid (form preserves input order). Tag each
        # code with its bucket so the sidebar can colour it.
        confirmed_set = {c.strip().upper() for c in confirmed}
        already_set = {c.strip().upper() for c in already_confirmed}
        invalid_set = {c.strip().upper() for c in invalid}
        last_codes: list[tuple[str, str]] = []
        for raw_code in stock_codes:
            code = raw_code.strip().upper()
            if code in confirmed_set:
                label = "confirmed"
            elif code in already_set:
                label = "already confirmed"
            elif code in invalid_set:
                label = "invalid"
            else:
                # Shouldn't happen — every submitted code lands in exactly
                # one of the three buckets. Fall through defensively.
                label = "invalid"
            last_codes.append((code, label))

        if confirmed:
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Successfully confirmed {len(confirmed)} stock items. ",
            )
        if already_confirmed:
            # NOTE: a physical bottle cannot be in two pharmacists' hands at
            # once, so seeing items in this bucket means another session
            # received the same code between this user opening the scan
            # page and submitting. Bucketing it as already_confirmed is the
            # intentional behaviour — see DESIGN_transaction_log.md.
            messages.add_message(
                request,
                messages.WARNING,
                f"Skipped {len(already_confirmed)} items. Stock items are already confirmed.",
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
            last_codes=last_codes,
            last_scanned_count=len(stock_codes),
            stock_transfer_pk=str(stock_transfer.pk),
        )

        # Multi-page scan loop: decrement the target by however many
        # inputs the user submitted this page (typically
        # SCAN_GRID_PAGE_SIZE, or fewer on the final page). Floor at 0
        # and additionally clamp against unconfirmed_items so that if
        # someone else confirmed bottles concurrently the user isn't
        # asked to scan more than physically remain.
        scanned_this_page = len(stock_codes)
        next_items_to_scan = max(0, prev_items_to_scan - scanned_this_page)
        next_items_to_scan = min(next_items_to_scan, stock_transfer.unconfirmed_items)
        url = reverse(
            "edc_pharmacy:confirm_at_location_url",
            kwargs={
                "session_uuid": str(session_uuid),
                "stock_transfer_identifier": stock_transfer_identifier,
                "location_id": location_id,
                "items_to_scan": next_items_to_scan,
            },
        )
        return HttpResponseRedirect(url)
