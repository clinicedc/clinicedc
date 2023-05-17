from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_lab_admin
from ..forms import ManifestItemForm
from ..models import ManifestItem
from .base_model_admin import BaseModelAdmin


class ManifestItemInlineAdmin(admin.TabularInline):
    model = ManifestItem
    form = ManifestItemForm
    extra = 1


@admin.register(ManifestItem, site=edc_lab_admin)
class ManifestItemAdmin(BaseModelAdmin, admin.ModelAdmin):
    form = ManifestItemForm

    fieldsets = (
        (None, {"fields": ("manifest", "identifier", "comment")}),
        audit_fieldset_tuple,
    )

    list_display = ("identifier",)

    def get_list_display(self, request) -> tuple:
        list_display = super().get_list_display(request)
        return tuple(set(("identifier",) + list_display))
