from django.apps import apps as django_apps
from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from .admin_site import edc_crf_admin
from .models import CrfStatus

crf_status_fieldset_tuple = (
    "CRF status",
    {"fields": ("crf_status", "crf_status_comments")},
)


class CrfStatusModelAdminMixin:
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if "crf_status" not in list_display:
            list_display = list(list_display)
            list_display.append("crf_status")
        return list_display

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if "crf_status" not in list_filter:
            list_filter = list(list_filter)
            list_filter.insert(0, "crf_status")
        return list_filter


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
