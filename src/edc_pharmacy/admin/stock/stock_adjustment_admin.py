from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...models import StockAdjustment
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockAdjustment, site=edc_pharmacy_admin)
class StockAdjustmentAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock adjustment"
    change_form_title = "Pharmacy: Stock adjustment"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    show_form_tools = True
    show_history_label = True
    autocomplete_fields = ["stock"]

    # form = StockAdjustmentForm

    ordering = ("-adjustment_datetime",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "stock",
                    "adjustment_datetime",
                    "unit_qty_in_old",
                    "unit_qty_in_new",
                    "reason",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "formatted_code",
        "adjustment_datetime",
        "unit_qty_in_old",
        "unit_qty_in_new",
        "reason",
        "created",
        "modified",
    )
    list_filter = (
        ("adjustment_datetime", DateRangeFilterBuilder()),
        "created",
        "modified",
    )
    search_fields = (
        "stock__stock_identifier",
        "stock__code",
    )

    @admin.display(description="Stock #", ordering="stock__code")
    def formatted_code(self, obj):
        return obj.stock.code

    @admin.display(description="From stock #", ordering="from_stock__code")
    def stock_changelist(self, obj):
        if obj.stock:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
            url = f"{url}?q={obj.stock.code}"
            context = dict(
                url=url,
                label=obj.stock.code,
                title="Go to stock",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None
