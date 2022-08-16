from django.contrib import admin
from edc_appointment.models import Appointment
from edc_data_manager.modeladmin_mixins import DataManagerModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_metadata_admin
from ..models import RequisitionMetadata


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(
    DataManagerModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    admin.ModelAdmin,
):
    @staticmethod
    def seq(obj=None):
        return obj.visit_code_sequence

    def get_subject_dashboard_url_kwargs(self, obj):
        appointment = Appointment.objects.get(
            subject_identifier=obj.subject_identifier,
            schedule_name=obj.schedule_name,
            visit_schedule_name=obj.visit_schedule_name,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
        )
        return dict(
            subject_identifier=obj.subject_identifier,
            appointment=appointment.id,
        )

    @staticmethod
    def panel(obj=None):
        return obj.panel_name

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
        "site",
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
