from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import ProductForm
from ..models import Product
from .model_admin_mixin import ModelAdminMixin


@admin.register(Product, site=edc_pharmacy_admin)
class ProductAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = ProductForm

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
                        "medication_lot",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "product_identifier",
        "container",
        "count_per_container",
        "formulation",
        "medication_lot",
        "created",
        "modified",
    )
    list_filter = (
        "formulation",
        "container",
    )
    search_fields = (
        "product_identifier",
        "medication_lot__lot_no",
    )
    ordering = (
        "product_identifier",
        "medication_lot__lot_no",
    )
    readonly_fields = ("product_identifier",)
