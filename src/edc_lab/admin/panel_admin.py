from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_lab_admin
from ..models import Panel
from .base_model_admin import BaseModelAdmin


@admin.register(Panel, site=edc_lab_admin)
class PanelAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': (
            'name', 'display_name', 'lab_profile_name')
        }),
        audit_fieldset_tuple,
    )

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + ('name', 'display_name', 'lab_profile_name')
        return fields
