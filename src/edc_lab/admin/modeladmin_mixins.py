from typing import Tuple
from uuid import UUID

from django.contrib import admin
from django.utils.html import format_html
from edc_constants.constants import YES

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

    search_fields = [
        "requisition_identifier",
        "subject_identifier",
        "panel__display_name",
    ]

    @staticmethod
    def visit_code(obj=None) -> str:
        return f"{obj.visit.visit_code}.{obj.visit.visit_code_sequence}"

    @staticmethod
    def requisition(obj=None):
        if obj.is_drawn == YES:
            return obj.requisition_identifier
        elif not obj.is_drawn:
            return format_html(
                '<span style="color:red;">{}</span>', obj.requisition_identifier
            )
        return format_html('<span style="color:red;">not drawn</span>')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "panel":
            pk = UUID(request.GET.get("panel")) if request.GET.get("panel") else None
            kwargs["queryset"] = db_field.related_model.objects.filter(pk=pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = ("requisition_datetime", "site", "is_drawn", "panel")
        list_filter = tuple(f for f in list_filter if f not in custom_fields)
        return custom_fields + list_filter

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "requisition",
            "subject_identifier",
            "visit_code",
            "panel",
            "requisition_datetime",
            "hostname_created",
        )
        list_display = tuple(f for f in list_display if f not in custom_fields)
        return custom_fields + list_display

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(
            set(readonly_fields + requisition_identifier_fields + requisition_verify_fields)
        )
