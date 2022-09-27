from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_protocol_incident_admin
from ..forms import ProtocolIncidentForm
from ..models import ProtocolIncident


@admin.register(ProtocolIncident, site=edc_protocol_incident_admin)
class ProtocolIncidentAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    form = ProtocolIncidentForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "short_description",
                    "report_type",
                )
            },
        ),
        (
            "Details of protocol incident",
            {
                "fields": (
                    "safety_impact",
                    "safety_impact_details",
                    "study_outcomes_impact",
                    "study_outcomes_impact_details",
                    "incident_datetime",
                    "incident",
                    "incident_other",
                    "incident_description",
                    "incident_reason",
                )
            },
        ),
        (
            "Actions taken",
            {
                "fields": (
                    "corrective_action_datetime",
                    "corrective_action",
                    "preventative_action_datetime",
                    "preventative_action",
                    "action_required",
                )
            },
        ),
        (
            "Report status",
            {
                "fields": (
                    "report_status",
                    "report_closed_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "action_required": admin.VERTICAL,
        "report_status": admin.VERTICAL,
        "report_type": admin.VERTICAL,
        "safety_impact": admin.VERTICAL,
        "study_outcomes_impact": admin.VERTICAL,
    }

    list_filter = (
        "report_type",
        "safety_impact",
        "study_outcomes_impact",
        "report_status",
    )

    list_display = (
        "subject_identifier",
        "dashboard",
        "report_type",
        "safety_impact",
        "study_outcomes_impact",
        "report_status",
    )

    search_fields = ("subject_identifier",)
