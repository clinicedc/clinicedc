from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from edc_model_admin.dashboard import ModelAdminDashboardMixin
from edc_model_admin.mixins import TemplatesModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin
from edc_visit_schedule.admin import ScheduleStatusListFilter
from edc_visit_tracking.utils import get_related_visit_model_cls

from .qa_report_modeladmin_mixin import QaReportModelAdminMixin


class OnStudyMissingValuesModelAdminMixin(
    QaReportModelAdminMixin,
    SiteModelAdminMixin,
    ModelAdminDashboardMixin,
    TemplatesModelAdminMixin,
):
    include_note_column: bool = True
    site_list_display_insert_pos: int = 2
    qa_report_list_display_insert_pos = 4
    ordering = ["site", "subject_identifier"]

    list_display = [
        "dashboard",
        "render_button",
        "subject",
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

    @admin.display(description="Update")
    def render_button(self, obj=None):
        crf_model_cls = django_apps.get_model(obj.label_lower)
        try:
            django_apps.get_model(obj.label_lower).objects.get(id=obj.original_id)
        except ObjectDoesNotExist:
            url = reverse(
                f"{self.crf_admin_site_name(crf_model_cls)}:"
                f"{obj.label_lower.replace('.', '_')}_add"
            )
            url = (
                f"{url}?next={self.admin_site.name}:"
                f"{self.model._meta.label_lower.replace('.', '_')}_changelist"
                f"&subject_identifier={obj.subject_identifier}"
                f"&subject_visit={obj.subject_visit_id}"
                f"&appointment={self.related_visit(obj).appointment.id}"
                f"&requisition={obj.original_id}"
            )
            title = _(f"Add {crf_model_cls._meta.verbose_name}")
            label = _("Add CRF")
            crf_button = render_to_string(
                "edc_qareports/columns/add_button.html",
                context=dict(title=title, url=url, label=label),
            )
        else:
            url = reverse(
                f"{self.crf_admin_site_name(crf_model_cls)}:"
                f"{obj.label_lower.replace('.', '_')}_change",
                args=(obj.original_id,),
            )
            url = (
                f"{url}?next={self.admin_site.name}:"
                f"{self.model._meta.label_lower.replace('.', '_')}_changelist"
            )
            title = _(f"Change {crf_model_cls._meta.verbose_name}")
            label = _("Change CRF")
            crf_button = render_to_string(
                "edc_qareports/columns/change_button.html",
                context=dict(title=title, url=url, label=label),
            )
        return crf_button

    def dashboard(self, obj=None, label=None) -> str:
        dashboard_url = reverse(
            self.get_subject_dashboard_url_name(obj=obj),
            kwargs=dict(
                subject_identifier=obj.subject_identifier,
                appointment=self.related_visit(obj).appointment.id,
            ),
        )
        context = dict(title=_("Go to subject's dashboard"), url=dashboard_url, label=label)
        return render_to_string("edc_subject_dashboard/dashboard_button.html", context=context)

    @staticmethod
    def crf_admin_site_name(crf_model_cls) -> str:
        """Returns the name of the admin site CRFs are registered
        by assuming admin site name follows the edc naming convention.

        For example: 'meta_subject_admin' or 'effect_subject_admin'
        """
        return f"{crf_model_cls._meta.label_lower.split('.')[0]}_admin"

    @staticmethod
    def related_visit(obj=None):
        return get_related_visit_model_cls().objects.get(id=obj.subject_visit_id)

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

    @admin.display(description="Subject", ordering="subject_identifier")
    def subject(self, obj) -> str | None:
        url = reverse(
            f"{self.admin_site.name}:{self.model._meta.label_lower.replace('.', '_')}"
            "_changelist"
        )
        return render_to_string(
            "edc_qareports/columns/subject_identifier_column.html",
            {
                "subject_identifier": obj.subject_identifier,
                "url": url,
                "title": _("Filter by subject"),
            },
        )
