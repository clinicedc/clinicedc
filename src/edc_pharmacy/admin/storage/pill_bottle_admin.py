from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin

# from ...forms import PillBottleForm
from ...models import PillBottle
from ..model_admin_mixin import ModelAdminMixin


@admin.register(PillBottle, site=edc_pharmacy_admin)
class PillBottleAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    # form = PillBottleForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "container_datetime",
                    "formulation",
                    "medication_lot",
                    "max_unit_qty",
                    "unit_qty",
                    "unit_qty_out",
                    "source_container",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_filter: Tuple[str, ...] = (
        "container_datetime",
        "medication_lot__lot_no",
        "formulation__medication__name",
        "created",
        "modified",
    )

    list_display: Tuple[str, ...] = (
        "container_identifier",
        "formulation",
        "medication_lot",
        "unit_qty",
        "unit_qty_out",
        "created",
        "modified",
    )

    search_fields: Tuple[str, ...] = (
        "medication_lot__lot_no",
        "formulation__medication__name",
    )

    ordering: Tuple[str, ...] = ("-expiration_date",)
