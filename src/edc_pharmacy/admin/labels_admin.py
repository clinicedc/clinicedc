from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import LabelsForm
from ..models import Labels
from .actions import print_medication_stock_labels
from .model_admin_mixin import ModelAdminMixin


@admin.register(Labels, site=edc_pharmacy_admin)
class LabelsAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = LabelsForm

    actions = [print_medication_stock_labels]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "medication_stock_create_labels",
                        "stock_identifier",
                        "printed",
                        "printed_datetime",
                        "in_stock",
                        "in_stock_datetime",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "medication_stock_create_labels",
        "stock_identifier",
        "printed",
        "printed_datetime",
        "in_stock",
        "in_stock_datetime",
        "created",
        "modified",
    ]
    list_filter = [
        "medication_stock_create_labels",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    ]
    search_fields = [
        "medication_stock_create_labels__medication_product__product_identifier",
        "medication_stock_create_labels__medication_product__lot_no",
    ]
    ordering = ["printed_datetime"]
    readonly_fields = [
        "medication_stock_create_labels",
        "stock_identifier",
        "printed",
        "printed_datetime",
        "in_stock",
        "in_stock_datetime",
    ]
