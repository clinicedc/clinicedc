from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import LotForm
from ...models import Lot
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Lot, site=edc_pharmacy_admin)
class LotAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = LotForm

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "lot_no",
                    "expiration_date",
                    "product",
                    "assignment",
                ]
            },
        ),
        audit_fieldset_tuple,
    )

    list_filter: Tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "product",
        "assignment",
        "created",
        "modified",
    )

    list_display: Tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "product",
        "assignment",
        "created",
        "modified",
    )
    radio_fields: Tuple[str, ...] = {"assignment": admin.VERTICAL}

    search_fields: Tuple[str, ...] = ("lot_no",)

    ordering: Tuple[str, ...] = ("-expiration_date",)
