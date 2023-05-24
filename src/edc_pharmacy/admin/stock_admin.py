from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import StockForm
from ..models import Stock
from .model_admin_mixin import ModelAdminMixin


@admin.register(Stock, site=edc_pharmacy_admin)
class StockAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = StockForm

    fieldsets = (
        (
            None,
            {"fields": ("stock_identifier", "product")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "stock_identifier",
        "product",
        "created",
        "modified",
    )
    list_filter = (
        "product",
        "product__medication_lot__lot_no",
        "product__formulation",
        "created",
        "modified",
    )
    search_fields = ("stock_identifier", "product__medication_lot__lot_no")
    ordering = ("stock_identifier",)
    readonly_fields = ("stock_identifier", "product")
