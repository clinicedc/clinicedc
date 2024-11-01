from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import StockForm
from ...models import Stock
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Stock, site=edc_pharmacy_admin)
class StockAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True
    show_form_tools = True
    autocomplete_fields = ["container", "receive_item"]

    form = StockForm

    fieldsets = (
        (
            None,
            {"fields": ("stock_identifier",)},
        ),
        (
            "Product",
            {"fields": ("product", "container")},
        ),
        (
            "Receive",
            {"fields": ("receive_item",)},
        ),
        (
            "Quantity",
            {
                "fields": (
                    "unit_qty_in",
                    "unit_qty_out",
                    "container_qty",
                    "container_qty_in",
                    "container_qty_out",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "product",
        "container",
        "unit_qty_in",
        "unit_qty_out",
        "container_qty",
        "container_qty_in",
        "container_qty_out",
        "created",
        "modified",
    )
    list_filter = (
        "product__name",
        "product__formulation",
        "created",
        "modified",
    )
    search_fields = ("stock_identifier", "product__name")
    ordering = ("stock_identifier",)
    readonly_fields = (
        "stock_identifier",
        "product",
        "unit_qty_in",
        "unit_qty_out",
        "container_qty",
        "container_qty_in",
        "container_qty_out",
    )

    @admin.display(description="Identifier", ordering="-stock_datetime")
    def identifier(self, obj):
        return obj.stock_identifier.split("-")[0]
