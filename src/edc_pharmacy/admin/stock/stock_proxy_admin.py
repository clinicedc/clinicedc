from django.contrib import admin

from ...admin_site import edc_pharmacy_admin
from ...models import StockProxy
from ..list_filters import TransferredListFilter
from .stock_admin import StockAdmin


@admin.register(StockProxy, site=edc_pharmacy_admin)
class StockProxyAdmin(StockAdmin):

    list_display = (
        "formatted_code",
        "transferred",
        "formatted_confirmed_at_site",
        "formatted_dispensed",
        "stock_request_changelist",
        "stock_transfer_item_changelist",
        "allocation_changelist",
        "dispense_changelist",
        "formulation",
        "qty",
        "container_str",
        "unit_qty",
        "created",
        "modified",
    )
    list_filter = (
        TransferredListFilter,
        "confirmed_at_site",
        "product__formulation__description",
        "location__display_name",
        "created",
        "modified",
    )
    search_fields = (
        "stock_identifier",
        "from_stock__stock_identifier",
        "code",
        "from_stock__code",
        "repack_request__id",
        "allocation__registered_subject__subject_identifier",
        "allocation__stock_request_item__id",
        "allocation__stock_request_item__stock_request__id",
        "allocation__id",
        "stocktransferitem__stock_transfer__id",
    )
    readonly_fields = (
        "code",
        "confirmed",
        "confirmed_by",
        "confirmed_datetime",
        "container",
        "from_stock",
        "location",
        "repack_request",
        "lot",
        "product",
        "qty_in",
        "qty_out",
        "unit_qty_in",
        "unit_qty_out",
        "receive_item",
        "stock_identifier",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(confirmed=True, allocation__isnull=False, container__may_request_as=True)
        )
