from django.contrib import admin
from django.utils.html import format_html
from edc_appointment.models import Appointment
from edc_data_manager.data_manager_modeladmin_mixin import DataManagerModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from edc_metadata import KEYED, REQUIRED

from ..admin_site import edc_metadata_admin
from ..exim_resources import CrfMetadataResource
from ..models import CrfMetadata


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(
    DataManagerModelAdminMixin, ModelAdminSubjectDashboardMixin, admin.ModelAdmin
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

    resource_class = CrfMetadataResource

    search_fields = ("subject_identifier", "model", "id")
    list_display = (
        "subject_identifier",
        "dashboard",
        "model",
        "visit_code",
        "seq",
        "status",
        "fill_datetime",
        "due_datetime",
        "close_datetime",
        "created",
        "hostname_created",
    )
    list_filter = (
        "entry_status",
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

    @staticmethod
    def status(obj=None):
        if obj.entry_status == REQUIRED:
            return format_html('<font color="orange">New</font>')
        if obj.entry_status == KEYED:
            return format_html('<font color="green">Keyed</font>')
        return obj.get_entry_status_display()
