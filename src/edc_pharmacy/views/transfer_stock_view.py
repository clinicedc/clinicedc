from django.apps import apps as django_apps
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

from ..models import Location, StockTransfer, StockTransferItem
from ..utils import transfer_stock


@method_decorator(login_required, name="dispatch")
class TransferStockView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    """A view for transferring stock from central to a site.

    Creates a StockTransferItem instance per stock instance.

    See also: StockTransferConfirmationItem
    """

    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/transfer_stock.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        stock_transfer = StockTransfer.objects.get(pk=self.kwargs.get("stock_transfer"))
        transferred_count = StockTransferItem.objects.filter(
            stock_transfer=stock_transfer
        ).count()
        item_count = stock_transfer.item_count - transferred_count
        item_count = 12 if item_count > 12 else item_count
        kwargs.update(
            stock_transfer=stock_transfer,
            source_model_name=self.model_cls._meta.verbose_name_plural,
            source_changelist_url=self.source_changelist_url,
            from_locations=Location.objects.filter(site__isnull=True),
            to_locations=Location.objects.filter(site__isnull=False),
            item_count=list(range(1, item_count + 1)),
        )
        return super().get_context_data(**kwargs)

    @property
    def source_changelist_url(self):
        return reverse("edc_pharmacy_admin:edc_pharmacy_stocktransfer_changelist")

    @property
    def model_cls(self):
        return django_apps.get_model("edc_pharmacy.stocktransfer")

    def post(self, request, *args, **kwargs):
        stock_transfer = StockTransfer.objects.get(pk=self.kwargs.get("stock_transfer"))
        stock_codes = request.POST.getlist("codes")
        if stock_codes:
            transferred, skipped_codes, invalid_codes = transfer_stock(
                stock_transfer, stock_codes, request=request
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Successfully transferred {len(transferred)} stock items. ",
            )
            if skipped_codes:
                messages.add_message(
                    request,
                    messages.WARNING,
                    f"Skipped {len(skipped_codes)}. Check location/site. Got {skipped_codes}",
                )
            if invalid_codes:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"{len(invalid_codes)} are invalid. Got {invalid_codes}",
                )

        transferred_count = StockTransferItem.objects.filter(
            stock_transfer=stock_transfer
        ).count()
        if stock_transfer.item_count > transferred_count:
            url = reverse(
                "edc_pharmacy:transfer_stock_url",
                kwargs={
                    "stock_transfer": stock_transfer.id,
                },
            )
            return HttpResponseRedirect(url)
        url = f"{self.source_changelist_url}"
        return HttpResponseRedirect(url)
