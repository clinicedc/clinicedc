from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import MedicationForm
from ...models import Medication
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Medication, site=edc_pharmacy_admin)
class MedicationAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = MedicationForm

    fieldsets = (
        (
            None,
            {"fields": ("name", "display_name", "notes")},
        ),
        audit_fieldset_tuple,
    )

    list_display: tuple[str, ...] = ("name", "display_name", "created", "modified")

    search_fields: tuple[str, ...] = ("name",)

    ordering: tuple[str, ...] = ("name",)
