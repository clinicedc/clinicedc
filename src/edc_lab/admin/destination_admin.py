from django.contrib import admin

from edc_base.modeladmin_mixins import (
    audit_fieldset_tuple, audit_fields)

from ..admin_site import edc_lab_admin
from ..models import Destination
from .base_model_admin import BaseModelAdmin


@admin.register(Destination, site=edc_lab_admin)
class DestinationAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'address',
                'tel',
                'email')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields
