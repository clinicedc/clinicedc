import inflect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from edc_utils import get_utcnow

from ..models import Stock, StorageBin, StorageBinItem
from .add_to_storage_bin_view import AddToStorageBinView, StorageBinError

p = inflect.engine()


def move_to_bin(
    storage_bin: StorageBin,
    stock_codes: list[str],
    user_modified: str,
    request: HttpRequest,
) -> tuple[list[str], list[str]]:
    codes_moved = []
    codes_not_moved = []
    # update storage bin capacity
    new_capacity = StorageBinItem.objects.filter(storage_bin=storage_bin).count() + len(
        stock_codes
    )
    if new_capacity > 50:
        raise StorageBinError(f"Storage bin {storage_bin.name} capacity may not exceeded 50")
    elif new_capacity > storage_bin.capacity:
        storage_bin.capacity = new_capacity
        storage_bin.save()
        messages.add_message(
            request,
            messages.INFO,
            f"Storage bin {storage_bin.name} capacity has been increased to {new_capacity}.",
        )
    # try to move codes to target bin
    for code in stock_codes:
        try:
            stock_obj = Stock.objects.get(
                code=code,
                allocation__isnull=False,
                confirmationatsiteitem__isnull=False,
                stored_at_site=True,
                dispenseitem__isnull=True,
                location=storage_bin.location,
            )
        except ObjectDoesNotExist:
            stock_obj = None
            codes_not_moved.append(code)
        if stock_obj:
            try:
                obj = StorageBinItem.objects.get(stock=stock_obj)
            except ObjectDoesNotExist:
                codes_not_moved.append(code)
            else:
                obj.storage_bin = storage_bin
                obj.user_modified = user_modified
                obj.modified = get_utcnow()
                obj.save()
                codes_moved.append(code)
    return codes_moved, codes_not_moved


@method_decorator(login_required, name="dispatch")
class MoveToStorageBinView(AddToStorageBinView):

    action_word = "Move"

    def redirect_on_stock_not_already_in_a_bin(
        self, stock_codes: list[str], storage_bin: StorageBin
    ) -> HttpResponseRedirect | None:
        if (
            stock_codes
            and Stock.objects.filter(
                code__in=stock_codes, storagebinitem__isnull=True
            ).exists()
        ):
            Stock.objects.filter(code__in=stock_codes, storagebinitem__isnull=True)
            messages.add_message(
                self.request,
                messages.ERROR,
                "Stock not found in any bin. Trying adding to storage bin first.",
            )
            url = reverse(
                "edc_pharmacy:move_to_storage_bin_url",
                kwargs={"storage_bin": storage_bin.id},
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
        self.redirect_on_stock_not_already_in_a_bin(stock_codes, storage_bin)
        if items_to_scan and not stock_codes:
            url = reverse(
                "edc_pharmacy:move_to_storage_bin_url",
                kwargs={
                    "storage_bin": storage_bin.id,
                    "items_to_scan": items_to_scan,
                },
            )
            return HttpResponseRedirect(url)
        elif items_to_scan and stock_codes:
            try:
                codes_moved, codes_not_moved = move_to_bin(
                    storage_bin, stock_codes, request.user.username, request
                )
            except StorageBinError as e:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    (
                        f"Moved {p.no('stock item', len(codes_moved))} "
                        f"to bin {storage_bin.name}. "
                        f"Skipped {len(codes_not_moved)}."
                    ),
                )
            return HttpResponseRedirect(self.storage_bin_changelist_url)
        url = reverse(
            "edc_pharmacy:move_to_storage_bin_url",
            kwargs={
                "storage_bin": storage_bin.id,
            },
        )
        return HttpResponseRedirect(url)
