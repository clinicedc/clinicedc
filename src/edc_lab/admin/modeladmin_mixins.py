from django.contrib import admin
from django.utils.safestring import mark_safe
from edc_constants.constants import YES
from uuid import UUID
from edc_lab.admin.fieldsets import (
    requisition_identifier_fields,
    requisition_verify_fields,
)


class RequisitionAdminMixin:

    ordering = ("requisition_identifier",)

    date_hierarchy = "requisition_datetime"

    radio_fields = {
        "is_drawn": admin.VERTICAL,
        "reason_not_drawn": admin.VERTICAL,
        "item_type": admin.VERTICAL,
    }

    list_display = [
        "requisition",
        "subject_identifier",
        "visit_code",
        "panel",
        "requisition_datetime",
        "hostname_created",
    ]

    list_filter = ["requisition_datetime", "site", "is_drawn", "panel"]

    search_fields = [
        "requisition_identifier",
        "subject_identifier",
        "panel__display_name",
    ]

    def visit_code(self, obj=None):
        return f"{obj.visit.visit_code}.{obj.visit.visit_code_sequence}"

    def requisition(self, obj=None):
        if obj.is_drawn == YES:
            return obj.requisition_identifier
        elif not obj.is_drawn:
            return mark_safe(
                f'<span style="color:red;">{obj.requisition_identifier}</span>'
            )
        return mark_safe('<span style="color:red;">not drawn</span>')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "panel":
            pk = UUID(request.GET.get("panel")) if request.GET.get("panel") else None
            kwargs["queryset"] = db_field.related_model.objects.filter(pk=pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            list(readonly_fields)
            + list(requisition_identifier_fields)
            + list(requisition_verify_fields)
        )
