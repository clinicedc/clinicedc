from __future__ import annotations

from django import forms
from django.contrib import admin
from import_export.admin import ExportMixin

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from ..admin_site import edc_metadata_admin
from ..models import CrfMetadata
from .modeladmin_mixins import MetadataModelAdminMixin
from .resources import CrfMetadataResource


class CrfMetadataForm(forms.ModelForm):
    class Meta:
        model = CrfMetadata
        fields = "__all__"
        verbose_name = "CRF collection status"


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(ExportMixin, MetadataModelAdminMixin):
    form = CrfMetadataForm
    resource_classes = [CrfMetadataResource]
    ordering = ()
    changelist_url = "edc_metadata_admin:edc_metadata_crfmetadata_changelist"
    change_list_title = "CRF collection status"
    change_form_title = "CRF collection status"
    include_audit_fields_in_list_filter = False
    include_audit_fields_in_list_display = False

    def has_export_permission(self, request):
        """Only users with the DATA_MANAGER role may export CrfMetadata."""
        try:
            roles = request.user.userprofile.roles
        except AttributeError:
            return False
        return roles.filter(name=DATA_MANAGER_ROLE).exists()
