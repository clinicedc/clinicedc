from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_fieldsets import Fieldset

from ..admin_site import edc_lab_admin
from ..forms import AliquotForm
from ..models import Aliquot
from .base_model_admin import BaseModelAdmin

aliquot_identifiers_fields = (
    "subject_identifier",
    "requisition_identifier",
    "parent_identifier",
    "identifier_prefix",
)

aliquot_identifiers_fieldset_tuple = Fieldset(
    *aliquot_identifiers_fields, section="Identifiers"
).fieldset


@admin.register(Aliquot, site=edc_lab_admin)
class AliquotAdmin(BaseModelAdmin, admin.ModelAdmin):
    form = AliquotForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "aliquot_identifier",
                    "aliquot_datetime",
                    "aliquot_type",
                    "numeric_code",
                    "alpha_code",
                    "condition",
                )
            },
        ),
        aliquot_identifiers_fieldset_tuple,
        ("Shipping", {"classes": ("collapse",), "fields": ("shipped",)}),
        audit_fieldset_tuple,
    )

    search_fields = ("aliquot_identifier", "subject_identifier")

    radio_fields = {"condition": admin.VERTICAL}

    def get_list_display(self, request) -> tuple:
        list_display = super().get_list_display(request)
        custom_fields = (
            "aliquot_identifier",
            "subject_identifier",
            "aliquot_datetime",
            "aliquot_type",
            "condition",
        )
        return tuple(set(custom_fields + list_display))

    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        custom_fields = ("aliquot_datetime", "aliquot_type", "condition")
        return tuple(set(custom_fields + list_filter))

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + aliquot_identifiers_fields))


class AliquotInlineAdmin(admin.TabularInline):
    model = Aliquot
    extra = 0
    fields = ("aliquot_identifier",)
