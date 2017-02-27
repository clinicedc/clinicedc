from django.contrib import admin

from edc_base.modeladmin_mixins import (
    audit_fieldset_tuple, audit_fields)

from ..admin_site import edc_lab_admin
from ..models import Manifest
from .base_model_admin import BaseModelAdmin


@admin.register(Manifest, site=edc_lab_admin)
class ManifestAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'manifest_datetime',
                'destination'
            )}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = ('manifest_identifier', 'manifest_datetime', 'destination')

    list_filter = ('manifest_datetime', )

    search_fields = ('manifest_identifier', )
