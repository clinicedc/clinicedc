from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_lab_admin
from ..forms import BoxItemForm
from ..models import BoxItem
from .base_model_admin import BaseModelAdmin


@admin.register(BoxItem, site=edc_lab_admin)
class BoxItemAdmin(BaseModelAdmin, admin.ModelAdmin):
    form = BoxItemForm

    fieldsets = (
        (None, {"fields": ("box", "position", "identifier", "comment")}),
        audit_fieldset_tuple,
    )

    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        custom_fields = ("identifier", "position")
        return tuple(set(custom_fields + list_filter))
