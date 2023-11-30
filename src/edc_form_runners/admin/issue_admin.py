from textwrap import wrap

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_sites.admin import SiteModelAdminMixin
from edc_visit_schedule.fieldsets import visit_schedule_only_fieldset_tuple

from ..admin_site import edc_form_runners_admin
from ..models import Issue
from .actions import issue_refresh


@admin.register(Issue, site=edc_form_runners_admin)
class IssueAdmin(
    SiteModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    admin.ModelAdmin,
):
    list_per_page = 15
    show_cancel = True
    actions = [issue_refresh]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "verbose_name",
                    "subject_identifier",
                    "visit_code",
                    "visit_code_sequence",
                    "src_report_datetime",
                    "src_revision",
                    "src_id",
                    "site",
                )
            },
        ),
        (
            "Message",
            {
                "fields": (
                    "field_name",
                    "label_lower",
                    "panel_name",
                    "message",
                    "raw_message",
                )
            },
        ),
        (
            "Session",
            {"fields": ("session_id", "session_datetime")},
        ),
        visit_schedule_only_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "dashboard",
        "document",
        "error_msg",
        "field_name",
        "response",
        "visit",
    )

    list_filter = (
        "visit_code",
        "visit_code_sequence",
        "panel_name",
        "verbose_name",
        "field_name",
        "short_message",
        "session_id",
        "session_datetime",
        "site",
    )

    readonly_fields = (
        "field_name",
        "label_lower",
        "message",
        "panel_name",
        "raw_message",
        "schedule_name",
        "session_datetime",
        "session_id",
        "site",
        "src_id",
        "src_modified_datetime",
        "src_report_datetime",
        "src_revision",
        "src_user_modified",
        "subject_identifier",
        "verbose_name",
        "visit_code",
        "visit_code_sequence",
        "visit_schedule_name",
    )

    search_fields = (
        "message",
        "label_lower",
        "field_name",
        "subject_identifier",
        "src_id",
    )

    @admin.display(description="Message", ordering="short_message")
    def error_msg(self, obj):
        return format_html("<BR>".join(wrap(obj.short_message, 45)).replace(" ", "&nbsp"))

    @admin.display(description="Visit", ordering="visit_code")
    def visit(self, obj):
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    @admin.display(description="Document", ordering="verbose_name")
    def document(self, obj):
        if obj.panel_name:
            return f"{obj.verbose_name.title()} {obj.panel_name.replace('_', ' ').title()}"
        return obj.verbose_name

    def get_subject_dashboard_url_kwargs(self, obj) -> dict:
        appointment_model_cls = django_apps.get_model("edc_appointment.appointment")
        try:
            appointment = appointment_model_cls.objects.get(
                subject_identifier=obj.subject_identifier,
                visit_code=obj.visit_code,
                visit_code_sequence=obj.visit_code_sequence,
                visit_schedule_name=obj.visit_schedule_name,
                schedule_name=obj.schedule_name,
            )
        except ObjectDoesNotExist:
            opts = dict(subject_identifier=obj.subject_identifier)
        else:
            opts = dict(
                subject_identifier=appointment.subject_identifier,
                appointment=str(appointment.id),
            )
        return opts
