from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import StockCreateLabelsForm
from ..models import StockCreateLabels
from .actions import print_stock_labels
from .model_admin_mixin import ModelAdminMixin


@admin.register(StockCreateLabels, site=edc_pharmacy_admin)
class StockCreateLabelsAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = StockCreateLabelsForm

    actions = [print_stock_labels]

    fieldsets = (
        (
            None,
            {"fields": ("product", "qty", "printed", "printed_datetime")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "product",
        "qty",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    )
    list_filter = (
        "product",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    )
    search_fields = (
        "product__product_identifier",
        "product__lot_no",
    )
    ordering = ("printed_datetime",)
    readonly_fields = ("printed", "printed_datetime")
