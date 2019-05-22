from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple, audit_fields

from ..admin_site import edc_lab_admin
from ..forms import BoxForm
from ..models import Box
from .base_model_admin import BaseModelAdmin


@admin.register(Box, site=edc_lab_admin)
class BoxAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "box_type",
                    "specimen_types",
                    "box_datetime",
                    "category",
                    "category_other",
                    "accept_primary",
                    "comment",
                )
            },
        ),
        (
            "Status",
            {
                "classes": ("collapse",),
                "fields": ("status", "verified", "verified_datetime"),
            },
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "box_type": admin.VERTICAL,
        "category": admin.VERTICAL,
        "status": admin.VERTICAL,
    }

    readonly_fields = ("status", "verified", "verified_datetime")

    list_display = (
        "box_identifier",
        "name",
        "category",
        "specimen_types",
        "box_type",
        "box_datetime",
        "user_created",
        "user_modified",
    )
