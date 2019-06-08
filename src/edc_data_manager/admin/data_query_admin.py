from django.conf import settings
from django.contrib import admin
from django.contrib.admin.decorators import register
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item.fieldsets import action_fieldset_tuple
from edc_appointment.models import Appointment
from edc_constants.constants import RESOLVED, OPEN, FEEDBACK, NEW
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_permissions.constants.group_names import DATA_MANAGER
from edc_utils import formatted_datetime

from ..admin_site import edc_data_manager_admin
from ..constants import RESOLVED_WITH_ACTION
from ..forms import DataQueryForm
from ..models import DataQuery


@register(DataQuery, site=edc_data_manager_admin)
class DataQueryAdmin(ModelAdminSubjectDashboardMixin,
                     SimpleHistoryAdmin):

    status_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/status.html")
    query_date_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/query_date.html")
    status_column_context = {
        "NEW": NEW,
        "OPEN": OPEN,
        "FEEDBACK": FEEDBACK,
        "RESOLVED": RESOLVED,
        "RESOLVED_WITH_ACTION": RESOLVED_WITH_ACTION,
    }

    show_cancel = True
    show_object_tools = True

    form = DataQueryForm

    radio_fields = {
        "status": admin.VERTICAL,
        "site_response_status": admin.VERTICAL,
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
        "subject",
        "query_dates",
        "sent_to",
        "site_status",
        "tcc_status",
        "query",
    )

    list_filter = ("site_response_status",
                   "status", "report_datetime",
                   "site_resolved_datetime",
                   "resolved_datetime")

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
            None,
            {
                "fields": (
                    "registered_subject",
                    "report_datetime",
                    "sender",
                    "recipient",
                )
            },
        ],
        [
            "Query",
            {
                "fields": (
                    "visit_schedule",
                    "visit_code_sequence",
                    "data_dictionaries",
                    "query_text",
                )
            },
        ],
        [
            "Site Response",
            {"fields": (
                "site_response_status",
                "site_response_text",
                "site_resolved_datetime",
            )},
        ],
        [
            "For TCC Only",
            {"fields": (
                "status",
                "resolved_datetime",
                "resolved_user",
                "plan_of_action",
            )},
        ],
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def query_dates(self, obj):
        context = dict(
            report_datetime=formatted_datetime(
                obj.report_datetime, settings.SHORT_DATE_FORMAT),
            site_resolved_datetime=formatted_datetime(
                obj.site_resolved_datetime, settings.SHORT_DATE_FORMAT),
            resolved_datetime=formatted_datetime(
                obj.resolved_datetime, settings.SHORT_DATE_FORMAT),
        )
        return self.render_query_date_to_string(context)

    def subject(self, obj):
        return self.dashboard(obj=obj, label=obj.subject_identifier)

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

    def site_status(self, obj):
        context = {
            "status": obj.site_response_status,
            "text": obj.get_site_response_status_display(),
        }
        return self.render_status_to_string(context)

    def tcc_status(self, obj):
        context = {
            "status": obj.status,
            "text": obj.get_status_display(),
        }
        return self.render_status_to_string(context)

    def render_status_to_string(self, context):
        context.update(self.status_column_context)
        return render_to_string(self.status_column_template_name, context=context)

    def render_query_date_to_string(self, context):
        return render_to_string(self.query_date_column_template_name, context=context)

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
                "status",
                "resolved_datetime",
                "resolved_user",
                "plan_of_action",
            ]
        return list(fields) + extra_fields

    def get_subject_dashboard_url_kwargs(self, obj):
        opts = dict(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule.visit_schedule_name,
            schedule_name=obj.visit_schedule.schedule_name,
            visit_code=obj.visit_schedule.visit_code,
            visit_code_sequence=obj.visit_code_sequence or 0,
        )
        try:
            appointment = Appointment.objects.get(**opts)
        except (ObjectDoesNotExist, AttributeError):
            kwargs = dict(subject_identifier=obj.subject_identifier)
        else:
            kwargs = dict(
                subject_identifier=obj.subject_identifier,
                appointment=str(appointment.pk))
        return kwargs

    def get_cancel_redirect_url(self, request=None, obj=None, **kwargs):
        return self.get_changelist_url(request=request, obj=obj, **kwargs)
