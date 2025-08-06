from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple

from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_reportable_admin
from ..models import NormalData


@admin.register(NormalData, site=edc_reportable_admin)
class NormalDataAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "label",
                    "units",
                    "gender",
                    "lower",
                    "lower_operator",
                    "lln",
                    "upper",
                    "upper_operator",
                    "uln",
                    "age_lower",
                    "age_lower_operator",
                    "age_upper",
                    "age_upper_operator",
                    "reference_range_collection",
                ]
            },
        ),
        audit_fieldset_tuple,
    )

    ordering = ("label", "units", "gender")
    list_display = (
        "label",
        "units",
        "gender",
        "range_desc",
        "age_desc",
        "collection",
        "auto_created",
        "created",
        "modified",
    )

    list_filter = (
        "reference_range_collection__name",
        "gender",
        "auto_created",
        "label",
        "units",
    )

    search_fields = ("label",)

    @admin.display(description="Range", ordering="lower")
    def range_desc(self, obj: NormalData) -> str | None:
        if obj and (obj.lower or obj.upper):
            return (
                f"{obj.lower or ''}{obj.lln or ''}{obj.lower_operator or ''}x"
                f"{obj.upper_operator or ''}{obj.upper or ''}{obj.uln or ''}"
            )
        return None

    @admin.display(description="Age", ordering="age_lower")
    def age_desc(self, obj: NormalData) -> str | None:
        if obj and obj.age_phrase:
            return obj.age_phrase % dict(age_value="x")
        return None

    @admin.display(description="Collection", ordering="collection__name")
    def collection(self, obj: NormalData) -> str | None:
        return obj.reference_range_collection.name
