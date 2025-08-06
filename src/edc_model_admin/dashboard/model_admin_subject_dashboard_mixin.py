from __future__ import annotations

from django.conf import settings
from django_audit_fields.admin import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_notification.modeladmin_mixins import NotificationModelAdminMixin

from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    TemplatesModelAdminMixin,
)

from .model_admin_dashboard_mixin import ModelAdminDashboardMixin


class ModelAdminSubjectDashboardMixin(
    ModelAdminDashboardMixin,
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    ModelAdminAuditFieldsMixin,
):
    date_hierarchy = "modified"
    empty_value_display = "-"
    list_per_page = 10
    show_cancel = True

    class Media:
        js = ("edc_model_admin/admin/js/delay_save_buttons.js",)

    def get_list_filter(self, request) -> tuple[str, ...]:
        return super().get_list_filter(request)

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        return super().get_readonly_fields(request, obj=obj)

    def get_search_fields(self, request) -> tuple[str, ...]:
        return super().get_search_fields(request)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["save_delay"] = getattr(
            settings, "EDC_MODEL_ADMIN_SAVE_DELAY", 0
        )  # milliseconds
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )
