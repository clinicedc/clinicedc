from typing import Tuple

from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from edc_constants.constants import CLOSED, OPEN

from edc_protocol_incident.constants import WITHDRAWN


class ProtocolIncidentModelAdminMixin:
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
                    "reasons_withdrawn",
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

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "description",
            "report_datetime",
            "status",
            "action_required",
            "report_type",
            "action_identifier",
            "user_created",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = ("action_required", "report_status", "report_type")
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        custom_fields = ("short_description",)
        return tuple(set(custom_fields + search_fields))

    def status(self, obj=None):
        color = None
        if obj.report_status == CLOSED:
            color = "green"
        elif obj.report_status == OPEN:
            color = "red"
        elif obj.report_status == WITHDRAWN:
            color = "darkorange"
        if color:
            return format_html(
                f'<span style="color:{color};">{obj.report_status.title()}</span>'
            )
        return obj.report_status.title()

    def description(self, obj=None):
        return obj.short_description.title()
