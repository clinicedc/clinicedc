from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

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

    def get_list_display(self, request) -> tuple:
        list_display = super().get_list_display(request)
        custom_fields = (
            "box_identifier",
            "name",
            "category",
            "specimen_types",
            "box_type",
            "box_datetime",
            "user_created",
            "user_modified",
        )
        return tuple(set(custom_fields + list_display))

    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        custom_fields = ("box_datetime", "specimen_types", "category", "box_type")
        return tuple(set(custom_fields + list_filter))

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + ("status", "verified", "verified_datetime")))
