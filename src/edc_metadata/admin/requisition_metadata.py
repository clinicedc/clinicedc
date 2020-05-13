from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from import_export.admin import ExportActionMixin

from ..admin_site import edc_metadata_admin
from ..exim_resources import RequisitionMetadataResource
from ..models import RequisitionMetadata


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(
    ModelAdminSubjectDashboardMixin, ExportActionMixin, admin.ModelAdmin,
):
    @staticmethod
    def seq(obj=None):
        return obj.visit_code_sequence

    @staticmethod
    def panel(obj=None):
        return obj.panel_name

    resource_class = RequisitionMetadataResource
    search_fields = ("subject_identifier", "model", "id", "panel_name")
    list_display = (
        "subject_identifier",
        "dashboard",
        "model",
        "panel",
        "visit_code",
        "seq",
        "entry_status",
        "fill_datetime",
        "due_datetime",
        "close_datetime",
        "created",
        "hostname_created",
    )
    list_filter = (
        "entry_status",
        "panel_name",
        "visit_code",
        "visit_code_sequence",
        "schedule_name",
        "visit_schedule_name",
        "model",
        "fill_datetime",
        "created",
        "user_created",
        "hostname_created",
    )
    readonly_fields = (
        "subject_identifier",
        "model",
        "visit_code",
        "schedule_name",
        "visit_schedule_name",
        "show_order",
        "current_entry_title",
    )
