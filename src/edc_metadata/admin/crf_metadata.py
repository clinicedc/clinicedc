from __future__ import annotations

from django import forms
from django.contrib import admin

from ..admin_site import edc_metadata_admin
from ..models import CrfMetadata
from .modeladmin_mixins import MetadataModelAdminMixin


class CrfMetadataForm(forms.ModelForm):
    class Meta:
        model = CrfMetadata
        fields = "__all__"
        verbose_name = "CRF collection status"


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(MetadataModelAdminMixin):
    form = CrfMetadataForm

    changelist_url = "edc_metadata_admin:edc_metadata_crfmetadata_changelist"
    change_list_title = "CRF collection status"
    change_form_title = "CRF collection status"
