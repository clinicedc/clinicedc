from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockTransferForm
from ...models import StockTransfer, StockTransferItem
from ..actions import print_transfer_stock_manifest_action, transfer_stock_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockTransfer, site=edc_pharmacy_admin)
class StockTransferAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Stock Transfer"
    change_form_title = "Pharmacy: Stock Transfers"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    autocomplete_fields = ["from_location", "to_location"]
    actions = [transfer_stock_action, print_transfer_stock_manifest_action]

    form = StockTransferForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_identifier",
                    "transfer_datetime",
                    "from_location",
                    "to_location",
                    "item_count",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "transfer_date",
        "from_location",
        "to_location",
        "item_count",
        "stock_transfer_item_changelist",
        "stock_changelist",
    )

    list_filter = (
        "transfer_datetime",
        "from_location",
        "to_location",
    )

    search_fields = ("id", "transfer_identifier")

    # readonly_fields = (
    #     "transfer_identifier",
    #     "transfer_datetime",
    #     "from_location",
    #     "to_location",
    #     "item_count",
    # )

    @admin.display(description="TRANSFER #", ordering="transfer_identifier")
    def identifier(self, obj):
        return obj.transfer_identifier

    @admin.display(description="Transfer date", ordering="transfer_datetime")
    def transfer_date(self, obj):
        return to_local(obj.transfer_datetime).date()

    @admin.display(description="Transfer items")
    def stock_transfer_item_changelist(self, obj):
        count = StockTransferItem.objects.filter(stock_transfer=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(
            url=url, label=f"Transfer items ({count})", title="Go to stock transfer items"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
