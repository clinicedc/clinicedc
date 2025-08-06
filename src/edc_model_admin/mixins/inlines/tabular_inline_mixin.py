from __future__ import annotations

from django.contrib import admin
from django_audit_fields.admin import ModelAdminAuditFieldsMixin


class TabularInlineMixin(ModelAdminAuditFieldsMixin, admin.TabularInline):
    insert_before_fieldset: str | None = "Audit"

    template = "edc_model_admin/admin/tabular.html"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.insert_before_fieldset = self.insert_before_fieldset
        return formset
