from django.contrib import admin
from django_audit_fields import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.mixins import (
    ModelAdminHideDeleteButtonOnCondition,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectAllToChangelistMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import edc_export_admin
from ..models import DataRequestHistory


@admin.register(DataRequestHistory, site=edc_export_admin)
class DataRequestHistoryAdmin(
    SiteModelAdminMixin,
    TemplatesModelAdminMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminRedirectAllToChangelistMixin,
    ModelAdminHideDeleteButtonOnCondition,
    admin.ModelAdmin,
):
    date_hierarchy = "exported_datetime"

    show_cancel = True
    view_on_site = False
    show_history_label = False

    change_search_field_name = "id"

    fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    list_display = (
        "data_request",
        "emailed_to",
        "emailed_datetime",
        "exported_datetime",
    )

    list_filter = ("emailed_to", "emailed_datetime", "exported_datetime")

    readonly_fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    search_fields = ("id", "summary", "archive_filename")

    def hide_delete_button_on_condition(self, request, object_id) -> bool:
        return True


class DataRequestHistoryInline(admin.TabularInline):
    model = DataRequestHistory

    fields = ("archive_filename", "emailed_to", "emailed_datetime", "exported_datetime")

    list_display = ("emailed_to", "exported_datetime", "created")

    readonly_fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    extra = 0
