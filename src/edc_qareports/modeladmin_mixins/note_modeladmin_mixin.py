from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
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

from ..forms import NoteForm


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
):
    """A modeladmin mixin class for the Note model."""

    form = NoteForm
    ordering = ("site", "subject_identifier")

    note_template_name = "edc_qareports/qa_report_note.html"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "note",
                    "status",
                )
            },
        ),
        (
            "Read-only",
            {
                "fields": (
                    "visit_code",
                    "visit_code_sequence",
                    "report_model",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "__str__",
        "dashboard",
        "report",
        "status",
        "report_note",
        "report_datetime",
    )

    radio_fields = {"status": admin.VERTICAL}  # noqa: RUF012

    list_filter = (
        "report_datetime",
        "status",
        "visit_code",
        "report_model",
        "user_created",
        "user_modified",
    )

    search_fields = ("subject_identifier", "report_model")

    @admin.display(description="Report", ordering="report_model")
    def report(self, obj=None):
        try:
            app_label, model = obj.report_model_cls._meta.label_lower.split(".")
        except (LookupError, ValueError):
            pass
        else:
            changelist_url = "_".join([app_label, model, "changelist"])
            try:
                # assume admin site naming convention
                url = reverse(f"{app_label}_admin:{changelist_url}")
            except NoReverseMatch:
                # TODO: find the admin site where this model is registered
                pass
            else:
                try:
                    obj.report_model_cls.objects.get(
                        subject_identifier=obj.subject_identifier,
                        visit_code=obj.visit_code or "",
                        visit_code_sequence=obj.visit_code_sequence or 0,
                        report_model=obj.report_model,
                    )
                except ObjectDoesNotExist:
                    return format_html(
                        '<a data-toggle="tooltip" title="go to report" href='
                        '"{url}">{report_model_cls}</a>. Data submitted',
                        url=url,
                        report_model_cls=obj.report_model_cls._meta.verbose_name,
                    )
                else:
                    return format_html(
                        '<a data-toggle="tooltip" title="go to report" href='
                        '"{url}?q={subject_identifier}">{report_model_cls}</a>',
                        url=url,
                        subject_identifier=obj.subject_identifier,
                        report_model_cls=obj.report_model_cls._meta.verbose_name,
                    )
        return obj.report_model

    @admin.display(description="QA Note", ordering="note")
    def report_note(self, obj=None):
        context = dict(note=obj.note)
        return render_to_string(self.note_template_name, context)
