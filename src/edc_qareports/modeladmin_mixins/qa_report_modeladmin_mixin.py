from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from edc_constants.constants import NEW
from edc_utils import truncate_string

from ..models import QaReportLog
from .list_filters import NoteStatusListFilter


class QaReportModelAdminMixin:
    """A mixin to link a data management report to a note (with status)
     on each report item.

    note_model_cls/template can be overridden in concrete classes.

    To use a custom Note model class, set `note_model_cls` to your
    custom model that uses the `NoteModelMixin`.
    """

    qa_report_log_enabled = True
    qa_report_list_display_insert_pos = 3
    list_per_page = 25
    note_model = "edc_qareports.note"
    note_status_list_filter = NoteStatusListFilter
    note_template = "edc_qareports/columns/notes_column.html"
    include_note_column = True

    @property
    def note_model_cls(self):
        return django_apps.get_model(self.note_model)

    def update_qa_report_log(self, request) -> None:
        QaReportLog.objects.create(
            username=request.user.username,
            site=request.site,
            report_model=self.model._meta.label_lower,
        )

    def changelist_view(self, request, extra_context=None):
        if self.qa_report_log_enabled:
            self.update_qa_report_log(request)
        return super().changelist_view(request, extra_context=extra_context)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display)
        if self.include_note_column:
            list_display.insert(self.qa_report_list_display_insert_pos, "notes")
            list_display.insert(self.qa_report_list_display_insert_pos, "status")
        return tuple(list_display)

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        list_filter = list(list_filter)
        if self.include_note_column:
            list_filter.insert(0, self.note_status_list_filter)
        return tuple(list_filter)

    def get_note_model_obj_or_raise(self, obj=None):
        try:
            note_model_obj = self.note_model_cls.objects.get(
                report_model=obj.report_model, subject_identifier=obj.subject_identifier
            )
        except ObjectDoesNotExist:
            raise
        return note_model_obj

    @admin.display(description="Status")
    def status(self, obj) -> str:
        try:
            note_model_obj = self.get_note_model_obj_or_raise(obj)
        except ObjectDoesNotExist:
            status = NEW
        else:
            status = note_model_obj.get_status_display()
        return status.title()

    @admin.display(description="Notes")
    def notes(self, obj=None) -> str:
        """Returns url to add or edit qa_report note model."""
        note_app_label, note_model_name = self.note_model_cls._meta.label_lower.split(".")
        note_url_name = f"{note_app_label}_{note_model_name}"

        report_app_label, report_model_name = self.model._meta.label_lower.split(".")
        next_url_name = "_".join([report_app_label, report_model_name, "changelist"])
        next_url_name = f"{report_app_label}_admin:{next_url_name}"

        try:
            note_model_obj = self.get_note_model_obj_or_raise(obj)
        except ObjectDoesNotExist:
            note_model_obj = None
            url = reverse(f"{note_app_label}_admin:{note_url_name}_add")
            title = _("Add if pending or cannot be resolved")
        else:
            url = reverse(
                f"{note_app_label}_admin:{note_url_name}_change",
                args=(note_model_obj.id,),
            )
            title = _("Edit if pending or cannot be resolved")

        url = (
            f"{url}?next={next_url_name},subject_identifier,q"
            f"&subject_identifier={obj.subject_identifier}"
            f"&report_model={obj.report_model}&q={obj.subject_identifier}"
        )
        label = self.get_notes_label(note_model_obj)
        context = dict(title=title, url=url, label=label)
        return render_to_string(self.note_template, context=context)

    def get_notes_label(self, obj) -> str:
        if not obj:
            label = _("Add")
        elif not obj.note:
            label = _("Edit")
        else:
            label = truncate_string(obj.note, max_length=35)
        return label
