from django.contrib import admin
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fields
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_fieldsets import FieldsetsModelAdminMixin
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
)


class BaseModelAdmin(
    ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminAuditFieldsMixin,
    FieldsetsModelAdminMixin,
    admin.ModelAdmin,
):
    list_per_page = 10
    date_hierarchy = "modified"
    empty_value_display = "-"
    view_on_site = False
    show_cancel = True

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + audit_fields + ("site",)))
