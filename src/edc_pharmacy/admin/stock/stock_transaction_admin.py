from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...models import StockTransaction
from ..model_admin_mixin import ModelAdminMixin
from .stock_transaction_resource import StockTransactionResource


@admin.register(StockTransaction, site=edc_pharmacy_admin)
class StockTransactionAdmin(ExportMixin, ModelAdminMixin, SimpleHistoryAdmin):
    resource_classes = [StockTransactionResource]
    change_list_title = "Pharmacy: Stock transaction ledger"
    change_form_title = "Pharmacy: Stock transaction"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    ordering = ("-transaction_datetime",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "stock",
                    "transaction_type",
                    "transaction_datetime",
                    "actor",
                    "reason",
                )
            },
        ),
        (
            "Quantities",
            {
                "fields": (
                    "qty_delta",
                    "unit_qty_delta",
                )
            },
        ),
        (
            "Locations",
            {
                "fields": (
                    "from_location",
                    "to_location",
                )
            },
        ),
        (
            "Allocations",
            {
                "classes": ("collapse",),
                "fields": (
                    "from_allocation",
                    "to_allocation",
                ),
            },
        ),
        (
            "Bins",
            {
                "classes": ("collapse",),
                "fields": (
                    "from_bin",
                    "to_bin",
                ),
            },
        ),
        (
            "Source objects",
            {
                "classes": ("collapse",),
                "fields": (
                    "receive_item",
                    "repack_request",
                    "stock_transfer_item",
                    "dispense_item",
                    "stock_adjustment",
                    "return_item",
                    "reverses",
                ),
            },
        ),
        (
            "State snapshot",
            {
                "classes": ("collapse",),
                "fields": ("state_after",),
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "txn_identifier",
        "stock_changelist",
        "transaction_type",
        "txn_date",
        "actor",
        "from_location",
        "to_location",
        "qty_delta",
        "unit_qty_delta",
        "reason",
        "created",
    )

    list_filter = (
        "transaction_type",
        ("transaction_datetime", DateRangeFilterBuilder()),
        "actor",
        ("created", DateRangeFilterBuilder()),
    )

    search_fields = (
        "stock__code",
        "stock__stock_identifier",
        "actor__username",
        "reason",
        "to_allocation__subject_identifier",
        "from_allocation__subject_identifier",
    )

    readonly_fields = (
        "stock",
        "transaction_type",
        "transaction_datetime",
        "actor",
        "reason",
        "qty_delta",
        "unit_qty_delta",
        "from_location",
        "to_location",
        "from_allocation",
        "to_allocation",
        "from_bin",
        "to_bin",
        "receive_item",
        "repack_request",
        "stock_transfer_item",
        "dispense_item",
        "stock_adjustment",
        "return_item",
        "reverses",
        "state_after",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Transaction", ordering="-transaction_datetime")
    def txn_identifier(self, obj):
        url = reverse(
            "edc_pharmacy_admin:edc_pharmacy_stocktransaction_change",
            args=[obj.pk],
        )
        context = dict(url=url, label=str(obj.pk)[:8], title="View transaction")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock #", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Date", ordering="transaction_datetime")
    def txn_date(self, obj):
        return to_local(obj.transaction_datetime).date()
