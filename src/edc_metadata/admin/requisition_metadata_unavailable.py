from __future__ import annotations

from django.contrib import admin
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple

from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_metadata_admin
from ..models import RequisitionMetadataUnavailable
from .list_filters import ScheduleNameListFilter

# natural-key fields are non-editable; show them readonly (records are created
# by the review detail view, not the admin)
READONLY = (
    "subject_identifier",
    "visit_schedule_name",
    "schedule_name",
    "visit_code",
    "visit_code_sequence",
    "model",
    "panel_name",
)

# FIELDS = (*READONLY, "reason", "comment", "decision_datetime", "site")


@admin.register(RequisitionMetadataUnavailable, site=edc_metadata_admin)
class RequisitionMetadataUnavailableAdmin(
    TemplatesModelAdminMixin, ModelAdminAuditFieldsMixin, SimpleHistoryAdmin
):
    show_object_tools = True
    ordering = ("subject_identifier", "visit_code", "model")

    fieldsets = (
        (None, {"fields": (*READONLY, "reason", "comment", "decision_datetime", "site")}),
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "model",
        "panel_name",
        "visit_code",
        "visit_code_sequence",
        "reason",
        "decision_datetime",
        "site",
    )
    list_filter = ("reason", "visit_code", ScheduleNameListFilter, "site")
    search_fields = ("subject_identifier", "model", "panel_name")
    readonly_fields = READONLY

    def has_add_permission(self, request) -> bool:  # noqa: ARG002
        return False
