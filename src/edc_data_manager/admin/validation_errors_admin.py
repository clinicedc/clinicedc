from textwrap import wrap

from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_data_manager_admin
from ..models import ValidationErrors
from .actions import (
    validation_error_flag_as_done,
    validation_error_flag_as_in_progress,
    validation_error_flag_as_new,
    validation_error_refresh,
)


@admin.register(ValidationErrors, site=edc_data_manager_admin)
class ValidationErrorsAdmin(
    SiteModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    admin.ModelAdmin,
):
    list_per_page = 15
    show_cancel = True
    actions = [
        validation_error_flag_as_done,
        validation_error_flag_as_in_progress,
        validation_error_flag_as_new,
        validation_error_refresh,
    ]

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
                    "message",
                    "raw_message",
                )
            },
        ),
        (
            "Session",
            {"fields": ("session_id", "session_datetime")},
        ),
        (
            "Status",
            {"fields": ("status",)},
        ),
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
        "status",
    )

    list_filter = (
        "verbose_name",
        "field_name",
        "visit_code",
        "visit_code_sequence",
        "status",
        "short_message",
        "session_id",
        "session_datetime",
        "site",
    )

    readonly_fields = (
        "session_id",
        "session_datetime",
        "verbose_name",
        "raw_message",
        "src_revision",
        "src_report_datetime",
        "src_modified_datetime",
        "src_user_modified",
        "subject_identifier",
        "visit_code",
        "visit_code_sequence",
        "site",
        "label_lower",
        "field_name",
        "message",
    )

    radio_fields = {
        "status": admin.VERTICAL,
    }

    search_fields = (
        "message",
        "label_lower",
        "field_name",
        "subject_identifier",
    )

    @admin.display(description="Message", ordering="short_message")
    def error_msg(self, obj):
        return format_html("<BR>".join(wrap(obj.short_message, 45)).replace(" ", "&nbsp"))

    @admin.display(description="Visit", ordering="visit_code")
    def visit(self, obj):
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    @admin.display(description="Document", ordering="verbose_name")
    def document(self, obj):
        return obj.verbose_name
