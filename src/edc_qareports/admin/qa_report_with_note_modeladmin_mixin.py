from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html
from edc_constants.constants import NEW

from ..models import QaReportNote
from .list_filters import QaNoteStatusListFilter


class QaReportWithNoteModelAdminMixin:
    """A mixin to link a data management report to notes and status
    on each report item.

    See also, model ReportNote.
    """

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display)
        list_display.insert(3, "notes")
        list_display.insert(3, "status")
        return tuple(list_display)

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        list_filter = list(list_filter)
        list_filter.insert(0, QaNoteStatusListFilter)
        return tuple(list_filter)

    @admin.display(description="Status", ordering="subject_identifier")
    def status(self, obj):
        try:
            report_note = self.get_qa_report_note_or_raise(obj)
        except ObjectDoesNotExist:
            return NEW
        return report_note.status

    @staticmethod
    def get_qa_report_note_or_raise(obj=None):
        try:
            qa_report_note = QaReportNote.objects.get(
                report_model=obj.report_model, subject_identifier=obj.subject_identifier
            )
        except ObjectDoesNotExist:
            raise
        return qa_report_note

    @admin.display(description="Notes", ordering="subject_identifier")
    def notes(self, obj=None):
        """Returns url to add or edit qa_report note"""
        url_name = "_".join(QaReportNote._meta.label_lower.split("."))
        app_label, model_name = self.model._meta.label_lower.split(".")
        next_url_name = "_".join([app_label, model_name, "changelist"])
        next_url_name = f"{app_label}_admin:{next_url_name}"
        try:
            qa_report_note = self.get_qa_report_note_or_raise(obj)
        except ObjectDoesNotExist:
            url = reverse(f"edc_qareports_admin:{url_name}_add")
            label = "Add"
            title = "Add report note"
        else:
            url = reverse(f"edc_qareports_admin:{url_name}_change", args=(qa_report_note.id,))
            label = qa_report_note.note[0:35] or "Edit"
            title = "Edit"
        url = (
            f"{url}?next={next_url_name},subject_identifier,q"
            f"&subject_identifier={obj.subject_identifier}"
            f"&report_model={obj.report_model}&q={obj.subject_identifier}"
        )
        return format_html(
            '<a data-toggle="tooltip" title="{}" href="{}">{}</a>',
            *(title, url, label),
        )
