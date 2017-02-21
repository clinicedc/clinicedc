from django.contrib import admin

from edc_base.modeladmin_mixins import (
    audit_fieldset_tuple, audit_fields)

from ..admin_site import edc_lab_admin
from ..models import SimpleBox
from .base_model_admin import BaseModelAdmin
from .box_item_admin import BoxItemInlineAdmin


@admin.register(SimpleBox, site=edc_lab_admin)
class SimpleBoxAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',)}),
        audit_fieldset_tuple)

    inlines = [BoxItemInlineAdmin]

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields
