from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_export_admin
from ..models import Plan


@admin.register(Plan, site=edc_export_admin)
class PlanAdmin(admin.ModelAdmin):

    fieldsets = (
        [None, {"fields": ("name", "model", "model_type")}],
        [
            "Export details",
            {
                "fields": (
                    "field_names",
                    "excluded_field_names",
                    "header_labels",
                    "lookups",
                    "header",
                    "encrypt",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = ("name", "model")
    list_filter = ("name", "model")
    search_fields = ("name", "model")
    radio_fields = {"model_type": admin.VERTICAL}
