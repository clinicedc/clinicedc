from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple, audit_fields

from ..admin_site import edc_lab_admin
from ..forms import ManifestForm
from ..models import Manifest
from .base_model_admin import BaseModelAdmin


@admin.register(Manifest, site=edc_lab_admin)
class ManifestAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = ManifestForm

    fieldsets = (
        (None, {
            'fields': (
                'manifest_datetime',
                'shipper',
                'consignee',
                'export_references',
                'status',
                'category',
                'category_other',
            )}),
        ('Site', {
            'classes': ('collapse',),
            'fields': (
                'site',
            )}),
        ('Shipping', {
            'classes': ('collapse',),
            'fields': (
                'shipped',
                'export_datetime',
            )}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + audit_fields
                + ('site', ))

    list_display = (
        'manifest_identifier', 'manifest_datetime', 'shipper', 'consignee')

    list_filter = ('manifest_datetime', )

    search_fields = ('manifest_identifier', )
