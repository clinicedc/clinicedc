from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import LabelsForm
from ..models import Labels
from .actions import print_stock_labels
from .model_admin_mixin import ModelAdminMixin


@admin.register(Labels, site=edc_pharmacy_admin)
class LabelsAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = LabelsForm

    actions = [print_stock_labels]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "stock_create_labels",
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

    list_display = (
        "stock_create_labels",
        "stock_identifier",
        "printed",
        "printed_datetime",
        "in_stock",
        "in_stock_datetime",
        "created",
        "modified",
    )
    list_filter = (
        "stock_create_labels",
        "printed",
        "printed_datetime",
        "created",
        "modified",
    )
    search_fields = (
        "stock_create_labels__product__product_identifier",
        "stock_create_labels__product__lot_no",
    )
    ordering = ("printed_datetime",)
    readonly_fields = (
        "stock_create_labels",
        "stock_identifier",
        "printed",
        "printed_datetime",
        "in_stock",
        "in_stock_datetime",
    )
