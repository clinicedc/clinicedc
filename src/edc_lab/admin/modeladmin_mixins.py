from typing import Tuple
from uuid import UUID

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from edc_constants.constants import UUID_PATTERN, YES
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_lab.admin.fieldsets import (
    requisition_identifier_fields,
    requisition_verify_fields,
)


class RequisitionAdminMixin:
    default_item_type = "tube"
    default_item_count = 1
    default_estimated_volume = 5.0

    ordering = ("requisition_identifier",)

    date_hierarchy = "requisition_datetime"

    radio_fields = {
        "is_drawn": admin.VERTICAL,
        "reason_not_drawn": admin.VERTICAL,
        "item_type": admin.VERTICAL,
    }

    search_fields: Tuple[str, ...] = (
        "requisition_identifier",
        "subject_identifier",
        "panel__display_name",
    )

    @staticmethod
    def visit_code(obj=None) -> str:
        return f"{obj.related_visit.visit_code}.{obj.related_visit.visit_code_sequence}"

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
            panel_id = request.GET.get("panel")
            if panel_id and UUID_PATTERN.match(panel_id):
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    pk=UUID(request.GET.get("panel"))
                )
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

    def get_changeform_initial_data(self, request) -> dict:
        initial_data = super().get_changeform_initial_data(request)
        if isinstance(request.GET.get(self.model.related_visit_model_attr()), UUID):
            try:
                related_visit = get_related_visit_model_cls().objects.get(
                    id=request.GET.get(self.model.related_visit_model_attr())
                )
            except ObjectDoesNotExist:
                # TODO: how do we get here? PRN?
                pass
            else:
                initial_data.update(
                    requisition_datetime=related_visit.report_datetime,
                    item_type=self.default_item_type,
                    item_count=self.default_item_count,
                    estimated_volume=self.default_estimated_volume,
                )
        return initial_data

        # if self.fields.get("specimen_type"):
        #     self.fields["specimen_type"].widget.attrs["readonly"] = True
