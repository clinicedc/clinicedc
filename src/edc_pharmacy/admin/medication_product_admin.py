from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationProductForm
from ..models import MedicationProduct
from .model_admin_mixin import ModelAdminMixin


@admin.register(MedicationProduct, site=edc_pharmacy_admin)
class MedicationProductAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = MedicationProductForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "product_identifier",
                        "container",
                        "count_per_container",
                        "formulation",
                        "lot_no",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "product_identifier",
        "container",
        "count_per_container",
        "formulation",
        "lot_no",
        "created",
        "modified",
    ]
    list_filter = [
        "formulation",
        "container",
    ]
    search_fields = ["product_identifier", "lot_no"]
    ordering = ["product_identifier", "lot_no"]
    readonly_fields = ["product_identifier"]
