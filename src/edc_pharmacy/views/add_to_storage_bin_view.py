from __future__ import annotations

from datetime import datetime

import inflect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..exceptions import StorageBinError
from ..models import Stock, StorageBin, StorageBinItem

p = inflect.engine()


def update_bin(
    storage_bin: StorageBin,
    stock_codes: list[str],
    user_created: str | None = None,
    created: datetime | None = None,
) -> tuple[list[str], list[str]]:
    codes_created = []
    codes_not_created = []
    for code in stock_codes:
        try:
            stock_obj = Stock.objects.get(
                code=code,
                allocation__isnull=False,
                stocktransferitem__isnull=False,
                confirmationatsiteitem__isnull=False,
                dispenseitem__isnull=True,
                location=storage_bin.location,
            )
        except ObjectDoesNotExist:
            stock_obj = None
            codes_not_created.append(code)
        if stock_obj:
            try:
                StorageBinItem.objects.get(stock=stock_obj)
            except ObjectDoesNotExist:
                StorageBinItem.objects.create(
                    stock=stock_obj,
                    storage_bin=storage_bin,
                    user_created=user_created,
                    created=created,
                )
                codes_created.append(code)
            else:
                codes_not_created.append(code)
    return codes_created, codes_not_created


@method_decorator(login_required, name="dispatch")
class AddToStorageBinView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/add_to_storage_bin.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"
    action_word = "Add"

    def get_context_data(self, **kwargs):
        kwargs.update(
            storage_bin=self.storage_bin,
            storage_bin_changelist_url=self.storage_bin_changelist_url,
            items_to_scan_as_range=[],
            SHORT_DATE_FORMAT=settings.SHORT_DATE_FORMAT,
            action_word=self.action_word,
        )
        if self.kwargs.get("items_to_scan"):
            items_to_scan = int(self.kwargs.get("items_to_scan"))
            kwargs.update(items_to_scan_as_range=range(1, items_to_scan + 1))
        return super().get_context_data(**kwargs)

    @property
    def storage_bin(self):
        storage_bin_id = self.kwargs.get("storage_bin")
        try:
            storage_bin = StorageBin.objects.get(id=storage_bin_id)
        except ObjectDoesNotExist:
            storage_bin = None
            messages.add_message(self.request, messages.ERROR, "Invalid storage bin.")
        return storage_bin

    @property
    def storage_bin_changelist_url(self) -> str:
        if self.storage_bin:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebin_changelist")
            url = f"{url}?q={self.storage_bin.bin_identifier}"
            return url
        return "/"

    def redirect_on_has_duplicates(
        self, stock_codes: list[str], storage_bin: StorageBin
    ) -> HttpResponseRedirect | None:
        if len(stock_codes or []) != len(list(set(stock_codes or []))):
            messages.add_message(
                self.request,
                messages.ERROR,
                "Nothing saved. Duplicate codes detected in list. Please try again.",
            )
            url = reverse(
                "edc_pharmacy:add_to_storage_bin_url",
                kwargs={
                    "stock_request": storage_bin.id,
                },
            )
            return HttpResponseRedirect(url)
        return None

    def redirect_on_stock_already_in_bin(
        self, stock_codes: list[str], storage_bin: StorageBin
    ) -> HttpResponseRedirect | None:
        if (
            stock_codes
            and StorageBinItem.objects.filter(stock__code__in=stock_codes)
            .exclude(storage_bin_id=storage_bin.id)
            .exists()
        ):
            qs = StorageBinItem.objects.filter(stock__code__in=stock_codes)
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Stock already in another bin. See {[obj.stock.code for obj in qs]}.",
            )
            url = reverse(
                "edc_pharmacy:add_to_storage_bin_url",
                kwargs={
                    "storage_bin": storage_bin.id,
                },
            )
            return HttpResponseRedirect(url)
        return None

    def redirect_on_invalid_subject_for_location(
        self, stock_codes: list[str], storage_bin: StorageBin
    ) -> HttpResponseRedirect | None:
        if stock_codes:
            if (
                Stock.objects.filter(code__in=stock_codes)
                .exclude(location=storage_bin.location)
                .exists()
            ):
                qs = Stock.objects.filter(code__in=stock_codes).exclude(
                    location=storage_bin.location
                )
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    f"Stock not from this location. See {[obj.stock.code for obj in qs]}.",
                )
                url = reverse(
                    "edc_pharmacy:add_to_storage_bin_url",
                    kwargs={
                        "storage_bin": storage_bin.id,
                    },
                )
                return HttpResponseRedirect(url)
        return None

    def post(self, request, *args, **kwargs):
        stock_codes = request.POST.getlist("codes") if request.POST.get("codes") else None
        storage_bin = StorageBin.objects.get(id=kwargs.get("storage_bin"))
        items_to_scan = request.POST.get("items_to_scan") or kwargs.get("items_to_scan")
        if items_to_scan:
            items_to_scan = int(items_to_scan)

        self.redirect_on_has_duplicates(stock_codes, storage_bin)
        self.redirect_on_invalid_subject_for_location(stock_codes, storage_bin)
        self.redirect_on_stock_already_in_bin(stock_codes, storage_bin)
        if items_to_scan and not stock_codes:
            url = reverse(
                "edc_pharmacy:add_to_storage_bin_url",
                kwargs={
                    "storage_bin": storage_bin.id,
                    "items_to_scan": items_to_scan,
                },
            )
            return HttpResponseRedirect(url)
        if items_to_scan and stock_codes:
            try:
                codes_created, codes_not_created = update_bin(
                    storage_bin,
                    stock_codes,
                    user_created=request.user.username,
                    created=timezone.now(),
                )
            except StorageBinError as e:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    (
                        f"Updated {p.no('stock item', len(codes_created))} to bin. "
                        f"Skipped {len(codes_not_created)}."
                    ),
                )
            return HttpResponseRedirect(self.storage_bin_changelist_url)
        url = reverse(
            "edc_pharmacy:add_to_storage_bin_url",
            kwargs={
                "storage_bin": storage_bin.id,
            },
        )
        return HttpResponseRedirect(url)
