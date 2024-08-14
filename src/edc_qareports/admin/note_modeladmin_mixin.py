from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.dashboard import ModelAdminDashboardMixin
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    TemplatesModelAdminMixin,
)
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_qareports_admin
from ..forms import QaReportNoteForm
from ..models import Note


@admin.register(Note, site=edc_qareports_admin)
class NoteModelAdminMixin(
    SiteModelAdminMixin,
    ModelAdminDashboardMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminNextUrlRedirectMixin,
    TemplatesModelAdminMixin,
    admin.ModelAdmin,
):
    """A modeladmin class for the QaReportNote model."""

    form = QaReportNoteForm
    ordering = ["site", "subject_identifier"]

    note_template_name = "edc_qareports/qa_report_note.html"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "note",
                    "status",
                    "subject_identifier",
                    "report_model",
                    "report_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "dashboard",
        "subject_identifier",
        "report",
        "status",
        "report_note",
        "report_datetime",
    ]

    radio_fields = {"status": admin.VERTICAL}

    list_filter = [
        "report_datetime",
        "status",
        "report_model",
        "user_created",
        "user_modified",
    ]

    search_fields = ["subject_identifier", "name"]

    @admin.display(description="Report", ordering="report_name")
    def report(self, obj=None):
        app_label, model = obj.report_model_cls._meta.label_lower.split(".")
        changelist_url = "_".join([app_label, model, "changelist"])
        try:
            # assume admin site naming convention
            url = reverse(f"{app_label}_admin:{changelist_url}")
        except NoReverseMatch:
            # TODO: find the admin site where this model is registered
            url = "#"
        return format_html(
            '<a data-toggle="tooltip" title="go to report" href="{}?q={}">{}</a>',
            *(url, obj.subject_identifier, obj.report_model_cls._meta.verbose_name),
        )

    @admin.display(description="QA Note", ordering="note")
    def report_note(self, obj=None):
        context = dict(note=obj.note)
        return render_to_string(self.note_template_name, context)

    def redirect_url(self, request, obj, post_url_continue=None) -> str | None:
        redirect_url = super().redirect_url(request, obj, post_url_continue=post_url_continue)
        return f"{redirect_url}?q={obj.subject_identifier}"
