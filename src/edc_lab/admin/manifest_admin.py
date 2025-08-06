from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_lab_admin
from ..forms import ManifestForm
from ..models import Manifest
from .base_model_admin import BaseModelAdmin


@admin.register(Manifest, site=edc_lab_admin)
class ManifestAdmin(BaseModelAdmin, admin.ModelAdmin):
    form = ManifestForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "manifest_datetime",
                    "shipper",
                    "consignee",
                    "export_references",
                    "status",
                    "category",
                    "category_other",
                )
            },
        ),
        ("Site", {"classes": ("collapse",), "fields": ("site",)}),
        (
            "Shipping",
            {"classes": ("collapse",), "fields": ("shipped", "export_datetime")},
        ),
        audit_fieldset_tuple,
    )

    search_fields = ("manifest_identifier",)

    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        return tuple(set(("manifest_datetime",) + list_filter))

    def get_list_display(self, request) -> tuple:
        list_display = super().get_list_display(request)
        custom_fields = ("manifest_identifier", "manifest_datetime", "shipper", "consignee")
        return tuple(set(custom_fields + list_display))
