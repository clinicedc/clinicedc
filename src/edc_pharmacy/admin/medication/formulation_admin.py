from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import FormulationForm
from ...models import Formulation
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Formulation, site=edc_pharmacy_admin)
class FormulationAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    autocomplete_fields = ["medication"]

    form = FormulationForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "medication",
                    "strength",
                    "units",
                    "formulation_type",
                    "route",
                    "description",
                )
            },
        ),
        (
            "Investigational medicinal product",
            {
                "fields": (
                    "imp",
                    "imp_description",
                )
            },
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "units": admin.VERTICAL,
        "formulation_type": admin.VERTICAL,
        "route": admin.VERTICAL,
    }

    list_filter: tuple[str, ...] = (
        "imp",
        "strength",
        "units",
        "formulation_type",
        "route",
    )

    list_display = (
        "description",
        "medication",
        "strength",
        "units",
        "formulation_type",
        "route",
    )

    search_fields: tuple[str, ...] = ("medication__name",)

    ordering: tuple[str, ...] = ("medication__name",)
