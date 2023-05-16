from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import StockReceivingForm
from ..models import StockReceiving
from .model_admin_mixin import ModelAdminMixin


@admin.register(StockReceiving, site=edc_pharmacy_admin)
class StockReceivingAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = StockReceivingForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "product",
                    "qty",
                    "stock_identifiers",
                    "received",
                    "received_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "product",
        "qty",
        "received",
        "received_datetime",
        "created",
        "modified",
    )
    list_filter = (
        "product",
        "received",
        "received_datetime",
        "created",
        "modified",
    )
    search_fields = ("product__product_identifier", "product__lot_no")
    ordering = ("received_datetime",)
    readonly_fields = ("received", "received_datetime")
