from __future__ import annotations

from django.contrib import admin
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple

from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ...admin_site import edc_metadata_admin
from ...models import RequisitionMetadataMissing
from ..list_filters import ScheduleNameListFilter
from .modeladmin_mixins import MissingModelAdminMixin


@admin.register(RequisitionMetadataMissing, site=edc_metadata_admin)
class RequisitionMetadataMissingAdmin(
    MissingModelAdminMixin,
    TemplatesModelAdminMixin,
    ModelAdminAuditFieldsMixin,
    SimpleHistoryAdmin,
):
    show_object_tools = True

    ordering = ("subject_identifier", "visit_code", "panel_name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "decision_datetime",
                    "visit_code",
                    "visit_code_sequence",
                    "model",
                    "panel_name",
                    "reason",
                    "site",
                    "visit_schedule_name",
                    "schedule_name",
                    "comment",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "model_verbose_name",
        "panel_name",
        "visit_as_string",
        "reason",
        "decision_datetime",
        "site",
    )

    list_filter = ("reason", "visit_code", "panel_name", ScheduleNameListFilter, "site")

    search_fields = ("subject_identifier", "model", "panel_name")

    readonly_fields = (
        "subject_identifier",
        "visit_schedule_name",
        "schedule_name",
        "visit_code",
        "visit_code_sequence",
        "model",
        "panel_name",
        "site",
    )
