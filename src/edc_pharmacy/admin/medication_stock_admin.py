from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationStockForm
from ..models import MedicationStock
from .model_admin_mixin import ModelAdminMixin


@admin.register(MedicationStock, site=edc_pharmacy_admin)
class MedicationStockAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = MedicationStockForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "stock_identifier",
                        "medication_product",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "stock_identifier",
        "medication_product",
        "created",
        "modified",
    ]
    list_filter = [
        "medication_product",
        "medication_product__lot_no",
        "medication_product__formulation",
        "created",
        "modified",
    ]
    search_fields = ["stock_identifier", "medication_product__lot_no"]
    ordering = ["stock_identifier"]
    readonly_fields = ["stock_identifier", "medication_product"]
