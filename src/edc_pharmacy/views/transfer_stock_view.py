from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import CENTRAL_LOCATION
from ..exceptions import StockTransferError
from ..models import StockTransfer, StockTransferItem
from ..utils import transfer_stock_to_location


@method_decorator(login_required, name="dispatch")
class TransferStockView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """Scan page for transferring stock items on a specific StockTransfer.

    Creates a StockTransferItem + TXN_TRANSFER_DISPATCHED transaction per
    scanned code.  The user scans codes one at a time via the JS accumulation
    UI and submits the batch.
    """

    template_name: str = "edc_pharmacy/stock/transfer_stock.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        stock_transfer = StockTransfer.objects.get(pk=self.kwargs.get("stock_transfer"))
        transfer_items = (
            StockTransferItem.objects.filter(stock_transfer=stock_transfer)
            .select_related(
                "stock__location",
                "stock__allocation",
                "stock_transfer__to_location",
            )
            .order_by("transfer_item_datetime")
        )
        transferred_count = transfer_items.count()
        remaining_count = max(0, stock_transfer.item_count - transferred_count)
        kwargs.update(
            stock_transfer=stock_transfer,
            transfer_items=transfer_items,
            transferred_count=transferred_count,
            remaining_count=remaining_count,
        )
        return super().get_context_data(**kwargs)

    @property
    def _home_url(self):
        return reverse("edc_pharmacy:stock_transfer_home_url")

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        stock_transfer = StockTransfer.objects.get(pk=self.kwargs.get("stock_transfer"))
        stock_codes = request.POST.getlist("codes")
        if stock_codes:
            transferred, dispensed_codes, skipped_codes, invalid_codes = [], [], [], []
            try:
                transferred, dispensed_codes, skipped_codes, invalid_codes = (
                    transfer_stock_to_location(stock_transfer, stock_codes, request=request)
                )
            except StockTransferError as e:
                messages.add_message(request, messages.ERROR, f"An error occurred. {e}")

            if transferred:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Successfully transferred {len(transferred)} stock item"
                    f"{'s' if len(transferred) != 1 else ''}.",
                )
            if skipped_codes:
                location = (
                    stock_transfer.to_location
                    if stock_transfer.from_location.name == CENTRAL_LOCATION
                    else stock_transfer.from_location
                )
                messages.add_message(
                    request,
                    messages.WARNING,
                    (
                        f"Skipped {len(skipped_codes)} "
                        f"stock item{'s' if len(skipped_codes) != 1 else ''}. "
                        f"Not allocated for {location}. "
                        f"Got: {', '.join(skipped_codes)}"
                    ),
                )
            if dispensed_codes:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Skipped {len(dispensed_codes)} stock item"
                    f"{'s' if len(dispensed_codes) != 1 else ''} — already dispensed. "
                    f"Got: {', '.join(dispensed_codes)}",
                )
            if invalid_codes:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Skipped {len(invalid_codes)} invalid code"
                    f"{'s' if len(invalid_codes) != 1 else ''}. "
                    f"Got: {', '.join(invalid_codes)}",
                )

        # Redirect back to scan page (more items remain) or home (complete).
        transferred_count = StockTransferItem.objects.filter(
            stock_transfer=stock_transfer
        ).count()
        if stock_transfer.item_count > transferred_count:
            return HttpResponseRedirect(
                reverse(
                    "edc_pharmacy:transfer_stock_url",
                    kwargs={"stock_transfer": stock_transfer.id},
                )
            )
        return HttpResponseRedirect(self._home_url)
