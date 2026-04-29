from __future__ import annotations

from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from rangefilter.filters import DateRangeFilterBuilder

from edc_appointment.utils import get_appointment_model_cls
from edc_dashboard.url_names import url_names
from edc_metadata import KEYED, REQUIRED
from edc_model_admin.mixins import (
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectAllToChangelistMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)
from edc_sites.admin import SiteModelAdminMixin

from .list_filters import (
    ScheduleNameListFilter,
    VisitCodeListFilter,
)


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
    change_list_note = (
        "Links to items from sites other than the current may not work as expected."
    )
    change_form_title = "CRF collection status"
    ordering = ("subject_identifier", "visit_code", "visit_code_sequence")

    view_on_site = True
    show_history_label = False
    list_per_page = 20
    show_full_result_count = False

    change_search_field_name = "subject_identifier"

    subject_dashboard_url_name = "subject_dashboard_url"  # url_name

    subject_review_dashboard_url_name = "subject_review_listboard_url"  # url_name

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

    search_fields = ("subject_identifier", "model", "document_name")
    list_display = (
        "subject_identifier",
        "dashboard",
        "document_name",
        "visit_code",
        "seq",
        "status",
        "due",
        "document_user",
        "created",
    )
    list_filter = (
        ("due_datetime", DateRangeFilterBuilder()),
        "entry_status",
        VisitCodeListFilter,
        "visit_code_sequence",
        ScheduleNameListFilter,
        # document_name intentionally dropped from the shared mixin.
        # Each concrete admin (CRF/Requisition) adds its own via
        # get_list_filter() so the option list is sourced from only the
        # relevant form collections.
        "site",
    )
    readonly_fields = (
        "subject_identifier",
        "model",
        "visit_code",
        "schedule_name",
        "visit_schedule_name",
        "show_order",
        "document_name",
        "document_user",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        appointment_model_cls = get_appointment_model_cls()
        appointment_subquery = appointment_model_cls.objects.filter(
            schedule_name=OuterRef("schedule_name"),
            site=OuterRef("site"),
            subject_identifier=OuterRef("subject_identifier"),
            visit_code=OuterRef("visit_code"),
            visit_code_sequence=OuterRef("visit_code_sequence"),
            visit_schedule_name=OuterRef("visit_schedule_name"),
        ).values("id")[:1]
        return qs.annotate(_appointment_id=Subquery(appointment_subquery))

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]

    @admin.display(description="Due", ordering="due_datetime")
    def due(self, obj):
        return obj.due_datetime

    @admin.display(description="Keyed", ordering="fill_datetime")
    def keyed(self, obj):
        return obj.fill_datetime

    def extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(show_cancel=True)
        return extra_context

    def get_subject_dashboard_url(self, obj=None) -> str | None:
        opts = {}
        if obj:
            appointment_id = getattr(obj, "_appointment_id", None)
            if appointment_id:
                opts = dict(appointment=str(appointment_id))
        return reverse(
            url_names.get(self.subject_dashboard_url_name),
            kwargs=dict(subject_identifier=obj.subject_identifier, **opts),
        )

    def dashboard(self, obj=None, label=None) -> str:
        url = self.get_subject_dashboard_url(obj=obj)
        context = dict(title="Go to subject's dashboard", url=url, label=label)
        return render_to_string("edc_subject_dashboard/dashboard_button.html", context=context)

    def get_subject_review_dashboard_url(self, obj=None) -> str | None:
        opts = {}
        if obj:
            appointment_id = getattr(obj, "_appointment_id", None)
            if appointment_id:
                opts = dict(appointment=str(appointment_id))
        return reverse(
            url_names.get(self.subject_review_dashboard_url_name),
            kwargs=dict(subject_identifier=obj.subject_identifier, **opts),
        )

    def subject_review_dashboard(self, obj=None, label=None) -> str:
        url = self.get_subject_review_dashboard_url(obj=obj)
        context = dict(title="Go to subject's review dashboard", url=url, label=label)
        return render_to_string("edc_subject_dashboard/dashboard_button.html", context=context)

    @staticmethod
    def seq(obj=None):
        return obj.visit_code_sequence

    @staticmethod
    def status(obj=None):
        if obj.entry_status == REQUIRED:
            return format_html(
                "{html}",
                html=mark_safe('<font color="orange">New</font>'),  # nosec B703, B308
            )
        if obj.entry_status == KEYED:
            return format_html(
                "{html}",
                html=mark_safe('<font color="green">Keyed</font>'),  # nosec B703, B308
            )
        return obj.get_entry_status_display()

    def get_view_on_site_url(self, obj=None) -> None | str:
        url = None
        if obj is None or not self.view_on_site:
            url = None
        if hasattr(obj, "get_absolute_url"):
            url = reverse(self.changelist_url)
            url = f"{url}?q={obj.subject_identifier}"
        return url
