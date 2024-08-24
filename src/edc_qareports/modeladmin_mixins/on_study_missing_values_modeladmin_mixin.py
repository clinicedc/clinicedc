from django.apps import apps as django_apps
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from edc_model_admin.dashboard import ModelAdminDashboardMixin
from edc_model_admin.mixins import TemplatesModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin
from edc_visit_schedule.admin import ScheduleStatusListFilter

from .qa_report_modeladmin_mixin import QaReportModelAdminMixin


class OnStudyMissingValuesModelAdminMixin(
    QaReportModelAdminMixin,
    SiteModelAdminMixin,
    ModelAdminDashboardMixin,
    TemplatesModelAdminMixin,
):
    include_note_column: bool = True
    project_reports_admin: str = "meta_reports_admin"
    project_subject_admin: str = "meta_subject_admin"

    ordering = ["site", "subject_identifier"]

    list_display = [
        "dashboard",
        "subject_identifier",
        "site",
        "label",
        "crf",
        "visit",
        "report_date",
        "created",
    ]

    list_filter = [
        ScheduleStatusListFilter,
        "label",
        "visit_code",
        "report_datetime",
    ]

    search_fields = ["subject_identifier", "label"]

    def dashboard(self, obj=None, label=None) -> str:
        url = self.get_subject_dashboard_url(obj=obj)
        if not url:
            url = reverse(
                f"{self.project_subject_admin}:{obj.label_lower.replace('.', '_')}_change",
                args=(obj.original_id,),
            )
            url = (
                f"{url}?next={self.project_reports_admin}:"
                f"{self.model._meta.label_lower.replace('.', '_')}_changelist"
            )
        context = dict(title=_("Go to CRF"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    @admin.display(description="CRF", ordering="label_lower")
    def crf(self, obj=None) -> str:
        model_cls = django_apps.get_model(obj.label_lower)
        return model_cls._meta.verbose_name

    @admin.display(description="Visit", ordering="visit_code")
    def visit(self, obj=None) -> str:
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    @admin.display(description="Report date", ordering="report_datetime")
    def report_date(self, obj) -> str | None:
        if obj.report_datetime:
            return obj.report_datetime.date()
        return None
