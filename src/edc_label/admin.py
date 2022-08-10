from typing import Tuple

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django_audit_fields import audit_fieldset_tuple

from .admin_site import edc_label_admin
from .models import ZplLabelTemplates


@admin.register(ZplLabelTemplates, site=edc_label_admin)
class ZplLabelTemplatesAdmin(ModelAdmin):
    fieldsets = (
        [None, {"fields": ("name", "zpl_data")}],
        audit_fieldset_tuple,
    )

    search_fields: Tuple[str, ...] = ("name",)
