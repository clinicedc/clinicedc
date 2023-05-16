from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationLotForm
from ..models import MedicationLot
from .model_admin_mixin import ModelAdminMixin


@admin.register(MedicationLot, site=edc_pharmacy_admin)
class MedicationLotAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = MedicationLotForm

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "lot_no",
                    "expiration_date",
                    "formulation",
                ]
            },
        ),
        audit_fieldset_tuple,
    )

    list_filter: Tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "formulation",
        "created",
        "modified",
    )

    list_display: Tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "formulation",
        "created",
        "modified",
    )

    search_fields: Tuple[str, ...] = ("lot_no",)

    ordering: Tuple[str, ...] = ("-expiration_date",)
