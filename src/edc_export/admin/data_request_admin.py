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
from edc_utils import get_utcnow

from ..admin_site import edc_export_admin
from ..forms import DataRequestForm
from ..models import DataRequest, DataRequestHistory
from .data_request_history_admin import DataRequestHistoryInline


@admin.register(DataRequest, site=edc_export_admin)
class DataRequestAdmin(
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
    show_cancel = True
    view_on_site = False
    show_history_label = False

    change_search_field_name = "id"

    actions = ("export_selected",)

    ordering = ("-created",)

    inlines = [DataRequestHistoryInline]

    form = DataRequestForm

    date_hierarchy = "created"

    fields = ("name", "models", "export_format", "decrypt")

    list_display = (
        "name",
        "description",
        "export_format",
        "decrypt",
        "user_created",
        "created",
    )

    list_filter = ("user_created", "created", "decrypt", "export_format")

    search_fields = ("id", "models", "description", "name")

    def export_selected(self, request, queryset):
        for obj in queryset:
            DataRequestHistory.objects.create(data_request=obj)
            rows_updated = queryset.update(exported_datetime=get_utcnow())
            if rows_updated == 1:
                message_bit = "1 data request was"
            else:
                message_bit = "%s data requests were" % rows_updated
            self.message_user(request, "%s successfully exported." % message_bit)

    export_selected.short_description = "Export selected data requests"

    def hide_delete_button_on_condition(self, request, object_id) -> bool:
        return True
