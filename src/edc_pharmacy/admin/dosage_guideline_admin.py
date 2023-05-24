from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import DosageGuidelineForm
from ..models import DosageGuideline
from .model_admin_mixin import ModelAdminMixin


@admin.register(DosageGuideline, site=edc_pharmacy_admin)
class DosageGuidelineAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    autocomplete_fields = ["medication"]

    form = DosageGuidelineForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "medication",
                    "dose",
                    "dose_per_kg",
                    "dose_units",
                    "frequency",
                    "frequency_units",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display: Tuple[str, ...] = ("__str__", "modified", "user_modified")
    search_fields: Tuple[str, ...] = ("medication__name",)
