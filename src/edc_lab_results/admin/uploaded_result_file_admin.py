from django.contrib import admin
from django_audit_fields.admin import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import (
    ModelAdminInstitutionMixin,
    TemplatesModelAdminMixin,
)

from ..admin_site import edc_lab_results_admin
from ..models import UploadedResultFile


@admin.register(UploadedResultFile, site=edc_lab_results_admin)
class UploadedResultFileAdmin(
    TemplatesModelAdminMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    ModelAdminAuditFieldsMixin,
    admin.ModelAdmin,
):
    date_hierarchy = "modified"
    empty_value_display = "-"

    list_display = (
        "original_filename",
        "stored_filename",
        "status",
        "uploaded_by",
        "uploaded_datetime",
        "imported_datetime",
    )
    list_filter = ("status",)
    search_fields = (
        "original_filename",
        "stored_filename",
    )
    readonly_fields = (
        "original_filename",
        "stored_filename",
        "status",
        "error_message",
        "uploaded_by",
        "uploaded_datetime",
        "imported_datetime",
    )
    ordering = ("-uploaded_datetime",)

    def has_add_permission(self, request: object) -> bool:  # noqa: ARG002
        return False

    def has_change_permission(
        self, request: object, obj: object = None  # noqa: ARG002
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: object = None  # noqa: ARG002
    ) -> bool:
        return False
