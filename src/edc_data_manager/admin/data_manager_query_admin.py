from django.contrib import admin
from django.contrib.admin.decorators import register
from django.core.exceptions import ObjectDoesNotExist
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item.fieldsets import action_fieldset_tuple
from edc_appointment.models import Appointment
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_permissions.constants.group_names import DATA_MANAGER

from ..admin_site import edc_data_manager_admin
from ..forms import DataManagerQueryForm
from ..models import DataManagerQuery


@register(DataManagerQuery, site=edc_data_manager_admin)
class DataManagerQueryAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    show_cancel = False
    show_object_tools = True

    form = DataManagerQueryForm

    radio_fields = {
        "resolved": admin.VERTICAL,
        "response_status": admin.VERTICAL,
    }

    autocomplete_fields = [
        "sender",
        "recipient",
        "data_dictionaries",
        "visit_schedule",
        "registered_subject",
        "resolved_user",
    ]

    list_display = (
        "reference",
        "subject_identifier",
        "dashboard",
        "report_datetime",
        "sent_to",
        "response_status",
        "resolved",
        "resolved_by",
        "query",
    )

    list_filter = ("report_datetime", "response_status",
                   "resolved", "resolved_datetime")

    search_fields = (
        "action_identifier",
        "sender__first_name",
        "sender__last_name",
        "sender__email",
        "sender__username",
        "recipient__first_name",
        "recipient__last_name",
        "recipient__email",
        "recipient__username",
        "registered_subject__subject_identifier",
    )

    fieldsets = (
        [
            "Query",
            {
                "fields": (
                    "registered_subject",
                    "report_datetime",
                    "sender",
                    "recipient",
                    "visit_schedule",
                    "data_dictionaries",
                    "query_text",
                )
            },
        ],
        [
            "Site Response",
            {"fields": ("response_datetime",
                        "response_text", "response_status")},
        ],
        [
            "For TCC Only",
            {"fields": ("resolved",
                        "resolved_datetime",
                        "resolved_user",
                        "plan_of_action")},
        ],
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def query(self, obj):
        return obj.query_text[:25] if obj.query_text else ""

    def dm(self, obj):
        return obj.sender.first_name

    def sent_to(self, obj):
        if obj.recipient:
            return f"{obj.recipient.first_name} {obj.recipient.last_name}"
        return None

    def resolved_by(self, obj):
        if obj.resolved_user:
            return f"{obj.resolved_user.first_name} {obj.resolved_user.last_name}"
        return None

    def reference(self, obj):
        return obj.action_identifier[-9:]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        extra_fields = []
        if not request.user.groups.filter(name=DATA_MANAGER):
            extra_fields = [
                "registered_subject",
                "report_datetime",
                "sender",
                "recipient",
                "visit_schedule",
                "data_dictionaries",
                "query_text",
            ]
        return list(fields) + extra_fields

    def get_subject_dashboard_url_kwargs(self, obj):
        try:
            Appointment.objects.get(
                subject_identifier=obj.subject_identifier,
                visit_schedule_name=obj.visit_schedule.visit_schedule_name,
                schedule_name=obj.visit_schedule.schedule_name,
                visit_code=obj.visit_schedule.visit_code)
        except (ObjectDoesNotExist, AttributeError):
            kwargs = dict(subject_identifier=obj.subject_identifier)
        else:
            kwargs = dict(
                subject_identifier=obj.subject_identifier,
                visit_schedule_name=obj.visit_schedule.visit_schedule_name,
                schedule_name=obj.visit_schedule.schedule_name,
                visit_code=obj.visit_schedule.visit_code)
        return kwargs
