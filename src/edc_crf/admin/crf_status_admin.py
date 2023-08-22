from django.apps import apps as django_apps
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_crf_admin
from ..models import CrfStatus

crf_status_fieldset_tuple = (
    _("CRF status"),
    {"fields": ("crf_status", "crf_status_comments")},
)


@admin.register(CrfStatus, site=edc_crf_admin)
class CrfStatusAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    list_display = (
        "subject_identifier",
        "crf",
        "dashboard",
        "visit",
        "schedule",
        "created",
    )

    list_filter = (
        "created",
        "user_created",
        "user_modified",
        "visit_code",
        "label_lower",
    )

    search_fields = ("subject_identifier",)

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule_name,
            schedule_name=obj.schedule_name,
            visit_code=obj.visit_code,
        )

    def visit(self, obj):
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    def crf(self, obj):
        model_cls = django_apps.get_model(obj.label_lower)
        return model_cls._meta.verbose_name

    def schedule(self, obj):
        return f"{obj.visit_schedule_name}.{obj.schedule_name}"
