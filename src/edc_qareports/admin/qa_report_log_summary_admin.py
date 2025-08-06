from django.apps import apps as django_apps
from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import ModelAdminInstitutionMixin, TemplatesModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_qareports_admin
from ..models import QaReportLogSummary


@admin.register(QaReportLogSummary, site=edc_qareports_admin)
class QaReportLogSummaryAdmin(
    SiteModelAdminMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    TemplatesModelAdminMixin,
    admin.ModelAdmin,
):
    ordering = ["-last_accessed"]

    list_display = (
        "username",
        "report",
        "hits",
        "first",
        "last",
        "report_model",
    )

    list_filter = ("last_accessed", "report_model", "username")

    search_fields = ("report_model", "username")

    readonly_fields = (
        "report_model",
        "username",
        "site",
        "first_accessed",
        "last_accessed",
        "access_count",
    )

    @admin.display(description="Report", ordering="report_model")
    def report(self, obj=None):
        try:
            model_cls = django_apps.get_model(obj.report_model)
        except LookupError:
            return obj.report_model
        return model_cls._meta.verbose_name

    @admin.display(description="Hits", ordering="access_count")
    def hits(self, obj=None):
        return obj.access_count

    @admin.display(description="First", ordering="first_accessed")
    def first(self, obj=None):
        return obj.first_accessed.strftime("%Y-%m-%d")

    @admin.display(description="Last", ordering="last_accessed")
    def last(self, obj=None):
        return obj.last_accessed.strftime("%Y-%m-%d")
