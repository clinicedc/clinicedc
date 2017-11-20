from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple, audit_fields

from ..admin_site import edc_lab_admin
from ..forms import BoxForm
from ..models import Box
from .base_model_admin import BaseModelAdmin


@admin.register(Box, site=edc_lab_admin)
class BoxAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'box_type',
                'specimen_types',
                'box_datetime',
                'category',
                'category_other',
                'accept_primary',
                'comment')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = (
        'box_identifier', 'name', 'category', 'specimen_types', 'box_type',
        'box_datetime', 'user_created', 'user_modified')
