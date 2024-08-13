from django.apps import apps as django_apps
from django.contrib import admin

from . import QaReportWithLinkedColumnModelAdminMixin


class QaReportWithNoteModelAdminMixin(QaReportWithLinkedColumnModelAdminMixin):
    """A mixin to link a data management report to notes and status
    on each report item.

    See also, model QaReportNote.
    """

    linked_model_cls = django_apps.get_model("edc_qareports.qareportnote")
    linked_column_field_name = "note"

    @admin.display(description="Notes")
    def linked_column(self, obj=None):
        """Returns url to add or edit qa_report model note"""
        return super().linked_column(obj=obj)
