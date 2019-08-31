from django.contrib import admin
from edc_model_admin.model_admin_audit_fields_mixin import (
    audit_fieldset_tuple,
    audit_fields,
)

from .admin_site import edc_randomization_admin
from .models import RandomizationList

admin.site.disable_action("delete_selected")


@admin.register(RandomizationList, site=edc_randomization_admin)
class RandomizationListModelAdmin(admin.ModelAdmin):

    ordering = ("sid",)

    list_display = (
        "subject_identifier",
        "sid",
        "site_name",
        "allocated_datetime",
        "allocated_site",
    )

    list_filter = ("allocated_datetime", "allocated_site", "site_name")

    search_fields = ("subject_identifier", "sid")

    readonly_fields = [
        "subject_identifier",
        "sid",
        "assignment",
        "allocated",
        "allocated_user",
        "allocated_datetime",
        "allocated_site",
    ] + audit_fields

    def get_fieldsets(self, request, obj=None):
        if obj and obj.subject_identifier:
            fieldsets = (
                (
                    None,
                    {
                        "fields": (
                            "subject_identifier",
                            "sid",
                            "assignment",
                            "allocated",
                            "allocated_user",
                            "allocated_datetime",
                            "allocated_site",
                        )
                    },
                ),
                audit_fieldset_tuple,
            )
        else:
            fieldsets = (
                (None, {"fields": ("subject_identifier", "sid", "allocated")}),
                audit_fieldset_tuple,
            )
        return fieldsets
