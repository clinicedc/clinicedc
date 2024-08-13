from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from edc_constants.constants import NEW

from ..models import QaReportLog
from ..utils import truncate_string
from .list_filters import QaReportLinkedColumnStatusListFilter


class QaReportWithLinkedColumnModelAdminMixin:
    """A mixin to link a data management report to a linked column
    (with status) on each report item.
    """

    qa_report_log_enabled = True
    qa_report_list_display_insert_pos = 3

    linked_model_cls = None
    linked_column_field_name = None

    linked_column_template = "edc_qareports/columns/linked_column.html"

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
        list_display.insert(self.qa_report_list_display_insert_pos, "linked_column")
        list_display.insert(self.qa_report_list_display_insert_pos, "status")
        return tuple(list_display)

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        list_filter = list(list_filter)
        list_filter.insert(0, QaReportLinkedColumnStatusListFilter)
        return tuple(list_filter)

    @admin.display(description="Status")
    def status(self, obj) -> str:
        try:
            linked_model_obj = self.get_linked_model_obj_or_raise(obj)
        except ObjectDoesNotExist:
            status = NEW
        else:
            status = linked_model_obj.status
        return status.title()

    def get_linked_model_obj_or_raise(self, obj=None):
        try:
            linked_model_obj = self.linked_model_cls.objects.get(
                report_model=obj.report_model, subject_identifier=obj.subject_identifier
            )
        except ObjectDoesNotExist:
            raise
        return linked_model_obj

    def linked_column(self, obj=None) -> str:
        """Returns url to add or edit qa_report linked model
        instance.
        """
        return self.render_linked_column_to_string(
            field_name=self.linked_column_field_name, obj=obj
        )

    def render_linked_column_to_string(self, field_name: str, obj=None) -> str:
        """Returns url to add or edit qa_report linked model."""
        linked_app_label, linked_model_name = self.linked_model_cls._meta.label_lower.split(
            "."
        )
        linked_url_name = f"{linked_app_label}_{linked_model_name}"

        report_app_label, report_model_name = self.model._meta.label_lower.split(".")
        next_url_name = "_".join([report_app_label, report_model_name, "changelist"])
        next_url_name = f"{report_app_label}_admin:{next_url_name}"

        try:
            linked_model_obj = self.get_linked_model_obj_or_raise(obj)
        except ObjectDoesNotExist:
            linked_model_obj = None
            url = reverse(f"{linked_app_label}_admin:{linked_url_name}_add")
            title = "Add"
        else:
            url = reverse(
                f"{linked_app_label}_admin:{linked_url_name}_change",
                args=(linked_model_obj.id,),
            )
            title = "Edit"

        url = (
            f"{url}?next={next_url_name},subject_identifier,q"
            f"&subject_identifier={obj.subject_identifier}"
            f"&report_model={obj.report_model}&q={obj.subject_identifier}"
        )
        label = self.get_linked_column_label(linked_model_obj, field_name)
        context = dict(title=title, url=url, label=label)
        return render_to_string(self.linked_column_template, context=context)

    def get_linked_column_label(self, obj, field_name=None):
        if not obj:
            label = "Add"
        else:
            label = getattr(obj, field_name) or "Edit"
            if isinstance(label, str):
                label = truncate_string(label, max_length=35)
        return label
