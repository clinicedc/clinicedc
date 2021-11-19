from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationStockReceivingForm
from ..models import MedicationStockReceiving
from .model_admin_mixin import ModelAdminMixin


@admin.register(MedicationStockReceiving, site=edc_pharmacy_admin)
class MedicationStockReceivingAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = MedicationStockReceivingForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "medication_product",
                        "qty",
                        "stock_identifiers",
                        "received",
                        "received_datetime",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "medication_product",
        "qty",
        "received",
        "received_datetime",
        "created",
        "modified",
    ]
    list_filter = [
        "medication_product",
        "received",
        "received_datetime",
        "created",
        "modified",
    ]
    search_fields = [
        "medication_product__product_identifier",
        "medication_product__lot_no",
    ]
    ordering = ["received_datetime"]
    readonly_fields = ["received", "received_datetime"]
