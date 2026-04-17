from django.contrib import admin

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_export.admin import ExportMixinModelAdminMixin

from ..admin_site import edc_metadata_admin
from ..models import RequisitionMetadata
from .modeladmin_mixins import MetadataModelAdminMixin
from .resources import RequisitionMetadataResource


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(ExportMixinModelAdminMixin, MetadataModelAdminMixin):
    resource_classes = [RequisitionMetadataResource]
    export_roles = (DATA_MANAGER_ROLE,)
    change_list_title = "Requisition collection status"
    change_form_title = "Requisition collection status"
    include_audit_fields_in_list_filter = False
    include_audit_fields_in_list_display = False

    @staticmethod
    def panel(obj=None):
        return obj.panel_name

    def get_search_fields(self, request):
        search_fields = list(super().get_search_fields(request))
        search_fields.append("panel_name")
        return tuple(search_fields)

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = list(super().get_list_display(request))
        list_display.insert(3, "panel_name")
        return tuple(list_display)

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = list(super().get_list_filter(request))
        list_filter.insert(1, "panel_name")
        return tuple(list_filter)
