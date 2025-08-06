from django.apps import apps as django_apps
from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import ModelAdminInstitutionMixin, TemplatesModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_qareports_admin
from ..models import QaReportLog


@admin.register(QaReportLog, site=edc_qareports_admin)
class QaReportLogAdmin(
    SiteModelAdminMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    TemplatesModelAdminMixin,
    admin.ModelAdmin,
):
    ordering = ["-accessed"]

    list_display = ["report", "username", "site", "accessed", "report_model"]

    list_filter = ["accessed", "report_model", "username", "site"]

    search_fields = ["report_model", "username"]

    readonly_fields = ["report_model", "username", "site", "accessed"]

    @admin.display(description="Report", ordering="report_model")
    def report(self, obj=None):
        model_cls = django_apps.get_model(obj.report_model)
        return model_cls._meta.verbose_name
