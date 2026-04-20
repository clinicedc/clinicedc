from __future__ import annotations

from django import forms
from django.contrib import admin

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_export.admin import ExportMixinModelAdminMixin

from ..admin_site import edc_metadata_admin
from ..models import CrfMetadata
from .list_filters import CrfDocumentNameListFilter, VisitScheduleNameListFilter
from .modeladmin_mixins import MetadataModelAdminMixin
from .resources import CrfMetadataResource


class CrfMetadataForm(forms.ModelForm):
    class Meta:
        model = CrfMetadata
        fields = "__all__"
        verbose_name = "CRF collection status"


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(ExportMixinModelAdminMixin, MetadataModelAdminMixin):
    form = CrfMetadataForm
    resource_classes = [CrfMetadataResource]
    export_roles = (DATA_MANAGER_ROLE,)
    ordering = ()
    changelist_url = "edc_metadata_admin:edc_metadata_crfmetadata_changelist"
    change_list_title = "CRF collection status"
    change_form_title = "CRF collection status"
    include_audit_fields_in_list_filter = False
    include_audit_fields_in_list_display = False

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = list(super().get_list_filter(request))
        list_filter.append(CrfDocumentNameListFilter)
        list_filter.append(VisitScheduleNameListFilter)
        return tuple(list_filter)
