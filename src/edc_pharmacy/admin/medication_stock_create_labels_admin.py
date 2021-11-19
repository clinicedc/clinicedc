from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationStockCreateLabelsForm
from ..models import MedicationStockCreateLabels
from .actions import print_medication_stock_labels
from .model_admin_mixin import ModelAdminMixin


@admin.register(MedicationStockCreateLabels, site=edc_pharmacy_admin)
class MedicationStockCreateLabelsAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = MedicationStockCreateLabelsForm

    actions = [print_medication_stock_labels]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "medication_product",
                        "qty",
                        # "randomizer",
                        # "allocation",
                        "printed",
                        "printed_datetime",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "medication_product",
        "qty",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    ]
    list_filter = [
        "medication_product",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    ]
    search_fields = [
        "medication_product__product_identifier",
        "medication_product__lot_no",
    ]
    ordering = ["printed_datetime"]
    readonly_fields = ["printed", "printed_datetime"]
