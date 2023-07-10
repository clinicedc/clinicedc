from typing import Tuple

from django.contrib import admin

from ..admin_site import edc_metadata_admin
from ..models import RequisitionMetadata
from .modeladmin_mixins import MetadataModelAdminMixin


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(MetadataModelAdminMixin):
    change_list_title = "Requisition collection status"
    change_form_title = "Requisition collection status"

    @staticmethod
    def panel(obj=None):
        return obj.panel_name

    def get_search_fields(self, request):
        search_fields = list(super().get_search_fields(request))
        search_fields.append("panel_name")
        return tuple(search_fields)

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = list(super().get_list_display(request))
        list_display.insert(3, "panel_name")
        return tuple(list_display)

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = list(super().get_list_filter(request))
        list_filter.insert(1, "panel_name")
        return tuple(list_filter)
