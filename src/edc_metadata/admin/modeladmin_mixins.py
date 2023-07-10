from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_appointment.utils import get_appointment_model_cls
from edc_dashboard import url_names
from edc_model_admin.mixins import (
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectAllToChangelistMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)
from edc_sites.admin import SiteModelAdminMixin

from edc_metadata import KEYED, REQUIRED


class MetadataModelAdminMixin(
    SiteModelAdminMixin,
    TemplatesModelAdminMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminRedirectAllToChangelistMixin,
    admin.ModelAdmin,
):
    changelist_url = "edc_metadata_admin:edc_metadata_crfmetadata_changelist"
    change_list_title = "CRF collection status"
    change_form_title = "CRF collection status"
    ordering = ["subject_identifier", "visit_code", "visit_code_sequence", "show_order"]

    view_on_site = True
    show_history_label = False

    change_search_field_name = "subject_identifier"

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "subject_identifier",
                    "entry_status",
                    "model",
                    "visit_code",
                    "visit_code_sequence",
                )
            },
        ],
        [
            "Status",
            {
                "fields": (
                    "report_datetime",
                    "due_datetime",
                    "fill_datetime",
                    "close_datetime",
                )
            },
        ],
        [
            "Timepoint",
            {
                "fields": (
                    "timepoint",
                    "schedule_name",
                    "visit_schedule_name",
                    "show_order",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    search_fields = ("subject_identifier", "model", "id")
    list_display = (
        "subject_identifier",
        "dashboard",
        "model_verbose_name",
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

    @admin.display(description="Model", ordering="model")
    def model_verbose_name(self, obj):
        return obj.model_cls()._meta.verbose_name

    def extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(show_cancel=True)
        return extra_context

    subject_dashboard_url_name = "subject_dashboard_url"

    def get_subject_dashboard_url(self, obj=None) -> str | None:
        opts = {}
        if obj:
            try:
                appointment = get_appointment_model_cls().objects.get(
                    schedule_name=obj.schedule_name,
                    site=obj.site,
                    subject_identifier=obj.subject_identifier,
                    visit_code=obj.visit_code,
                    visit_code_sequence=obj.visit_code_sequence,
                    visit_schedule_name=obj.visit_schedule_name,
                )
            except ObjectDoesNotExist:
                pass
            else:
                opts = dict(appointment=str(appointment.id))
        return reverse(
            url_names.get(self.subject_dashboard_url_name),
            kwargs=dict(subject_identifier=obj.subject_identifier, **opts),
        )

    def dashboard(self, obj=None, label=None) -> str:
        url = self.get_subject_dashboard_url(obj=obj)
        context = dict(title="Go to subject's dashboard", url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    @staticmethod
    def seq(obj=None):
        return obj.visit_code_sequence

    @staticmethod
    def status(obj=None):
        if obj.entry_status == REQUIRED:
            return format_html('<font color="orange">New</font>')
        if obj.entry_status == KEYED:
            return format_html('<font color="green">Keyed</font>')
        return obj.get_entry_status_display()

    def get_view_on_site_url(self, obj=None):
        if obj is None or not self.view_on_site:
            return None
        elif hasattr(obj, "get_absolute_url"):
            url = reverse(self.changelist_url)
            return f"{url}?q={obj.subject_identifier}"
