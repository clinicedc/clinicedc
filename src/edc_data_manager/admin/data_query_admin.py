from django.conf import settings
from django.contrib import admin
from django.contrib.admin.decorators import register
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item.fieldsets import action_fieldset_tuple, action_fields
from edc_appointment.models import Appointment
from edc_auth import DATA_MANAGER
from edc_constants.constants import (
    RESOLVED,
    OPEN,
    FEEDBACK,
    NEW,
    HIGH_PRIORITY,
    CLOSED,
    YES,
    NO,
)
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_utils import formatted_datetime
from textwrap import wrap

from ..admin_site import edc_data_manager_admin
from ..constants import CLOSED_WITH_ACTION
from ..forms import DataQueryForm
from ..models import DataQuery, DataDictionary


@register(DataQuery, site=edc_data_manager_admin)
class DataQueryAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    status_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/status.html"
    )
    query_date_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/query_date.html"
    )
    query_text_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/query_text.html"
    )
    query_recipients_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/"
        f"query_recipients.html"
    )

    rule_generated_column_template_name = (
        f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/columns/"
        f"rule_generated.html"
    )

    status_column_context = {
        "NEW": NEW,
        "OPEN": OPEN,
        "FEEDBACK": FEEDBACK,
        "RESOLVED": RESOLVED,
        "CLOSED": CLOSED,
        "CLOSED_WITH_ACTION": CLOSED_WITH_ACTION,
    }

    show_cancel = True
    show_object_tools = True

    form = DataQueryForm

    radio_fields = {
        "status": admin.VERTICAL,
        "site_response_status": admin.VERTICAL,
        "query_priority": admin.VERTICAL,
    }

    autocomplete_fields = [
        "sender",
        "recipients",
        "data_dictionaries",
        "requisition_panel",
        "visit_schedule",
        "registered_subject",
        "dm_user",
    ]

    list_display = (
        "wrapped_title",
        "subject",
        "query_status",
        "sent_to",
        "query",
        "generated",
        "created",
        "modified",
        "reference",
    )

    list_filter = (
        "site_response_status",
        "status",
        "query_priority",
        "report_datetime",
        "site_resolved_datetime",
        "resolved_datetime",
        "rule_generated",
        "title",
        "created",
        "modified",
    )

    search_fields = (
        "title",
        "action_identifier",
        "sender__first_name",
        "sender__last_name",
        "sender__email",
        "sender__username",
        "recipients__first_name",
        "recipients__last_name",
        "recipients__email",
        "recipients__username",
        "registered_subject__subject_identifier",
        "data_dictionaries__model_verbose_name",
        "data_dictionaries__prompt",
        "data_dictionaries__field_name",
        "data_dictionaries__number",
        "requisition_panel__name",
        "requisition_panel__display_name",
        "query_text",
        "site_response_text",
        "plan_of_action",
    )

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "registered_subject",
                    "report_datetime",
                    "sender",
                    "query_priority",
                    "recipients",
                )
            },
        ],
        [
            "Query Details",
            {
                "fields": (
                    "title",
                    "visit_schedule",
                    "visit_code_sequence",
                    "data_dictionaries",
                    "requisition_panel",
                    "query_text",
                )
            },
        ],
        [
            "Site Response",
            {
                "fields": (
                    "site_response_status",
                    "site_response_text",
                    "site_resolved_datetime",
                )
            },
        ],
        [
            "For Data Manager Only",
            {"fields": ("status", "resolved_datetime", "dm_user", "plan_of_action")},
        ],
        [
            "Rules",
            {"classes": ("collapse",), "fields": ("rule_generated", "rule_reference")},
        ],
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def wrapped_title(self, obj=None):
        wrapped_title = wrap(obj.title, width=20)
        return mark_safe("<BR>".join(wrapped_title))

    wrapped_title.short_description = "Title"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "data_dictionaries":
            if request.GET.get("title"):
                kwargs["queryset"] = DataDictionary.objects.filter(
                    model_verbose_name=request.GET.get("title")
                )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def query_dates(self, obj):
        context = dict(
            report_datetime=formatted_datetime(
                obj.report_datetime, settings.SHORT_DATE_FORMAT
            ),
            site_resolved_datetime=formatted_datetime(
                obj.site_resolved_datetime, settings.SHORT_DATE_FORMAT
            ),
            resolved_datetime=formatted_datetime(
                obj.resolved_datetime, settings.SHORT_DATE_FORMAT
            ),
        )
        return self.render_query_date_to_string(context)

    def subject(self, obj):
        return self.dashboard(obj=obj, label=obj.subject_identifier)

    def query(self, obj):
        context = dict(
            plane_of_action=obj.plan_of_action,
            report_datetime=formatted_datetime(
                obj.report_datetime, settings.SHORT_DATE_FORMAT
            ),
            site_resolved_datetime=formatted_datetime(
                obj.site_resolved_datetime, settings.SHORT_DATE_FORMAT
            ),
            resolved_datetime=formatted_datetime(
                obj.resolved_datetime, settings.SHORT_DATE_FORMAT
            ),
            visit_schedule=obj.visit_schedule,
            questions=obj.data_dictionaries.all().order_by("model", "number"),
            requisition_panel=obj.requisition_panel,
            site_response_text=obj.site_response_text,
            status=obj.status,
            dm_user=obj.dm_user,
            query_text=obj.query_text,
            query_priority_display=obj.get_query_priority_display(),
            query_priority=obj.query_priority,
            HIGH_PRIORITY=HIGH_PRIORITY,
            RESOLVED=RESOLVED,
            CLOSED=CLOSED,
            CLOSED_WITH_ACTION=CLOSED_WITH_ACTION,
        )
        return self.render_query_text_to_string(context)

    def dm(self, obj):
        return obj.sender.first_name

    def generated(self, obj):
        rule_generated = YES if obj.rule_generated else NO
        context = {"rule_generated": rule_generated, "YES": YES, "NO": NO}
        return self.render_rule_generated_to_string(context)

    def sent_to(self, obj):
        context = {"recipients": obj.recipients.all()}
        return self.render_query_recipients_to_string(context)

    def resolved_by(self, obj):
        if obj.dm_user:
            return f"{obj.dm_user.first_name} {obj.dm_user.last_name}"
        return None

    def reference(self, obj):
        return obj.action_identifier[-9:]

    def query_status(self, obj):
        context = {
            "site_response_status": obj.site_response_status,
            "dm_status": obj.status,
            "site_response_status_display": obj.get_site_response_status_display(),
            "dm_status_display": obj.get_status_display(),
        }
        return self.render_status_to_string(context)

    query_status.short_description = "Status"

    def render_status_to_string(self, context):
        context.update(self.status_column_context)
        return render_to_string(self.status_column_template_name, context=context)

    def render_rule_generated_to_string(self, context):
        return render_to_string(
            self.rule_generated_column_template_name, context=context
        )

    def render_query_date_to_string(self, context):
        return render_to_string(self.query_date_column_template_name, context=context)

    def render_query_text_to_string(self, context):
        return render_to_string(self.query_text_column_template_name, context=context)

    def render_query_recipients_to_string(self, context):
        return render_to_string(
            self.query_recipients_column_template_name, context=context
        )

    def created_details(self, obj):
        rule_generated = YES if obj.rule_generated else NO
        context = {
            "rule_generated": rule_generated,
            "YES": YES,
            "NO": NO,
            "created": obj.created,
            "modified": obj.modified,
            "reference": obj.action_identifier[-9:],
        }
        return render_to_string(self.query_date_column_template_name, context=context)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        extra_fields = ["rule_generated", "rule_reference", *action_fields]
        if not request.user.groups.filter(name=DATA_MANAGER):
            extra_fields = [
                "registered_subject",
                "report_datetime",
                "sender",
                "recipients",
                "visit_schedule",
                "data_dictionaries",
                "query_priority",
                "query_text",
                "status",
                "resolved_datetime",
                "dm_user",
                "plan_of_action",
            ]
        return list(fields) + extra_fields

    def get_subject_dashboard_url_kwargs(self, obj):
        def get_opts():
            return dict(
                subject_identifier=obj.subject_identifier,
                visit_schedule_name=obj.visit_schedule.visit_schedule_name,
                schedule_name=obj.visit_schedule.schedule_name,
                visit_code=obj.visit_schedule.visit_code,
                visit_code_sequence=obj.visit_code_sequence or 0,
            )

        try:
            appointment = Appointment.objects.get(**get_opts())
        except (ObjectDoesNotExist, AttributeError):
            kwargs = dict(subject_identifier=obj.subject_identifier)
        else:
            kwargs = dict(
                subject_identifier=obj.subject_identifier,
                appointment=str(appointment.pk),
            )
        return kwargs

    def get_cancel_redirect_url(self, request=None, obj=None, **kwargs):
        return self.get_changelist_url(request=request, obj=obj, **kwargs)
