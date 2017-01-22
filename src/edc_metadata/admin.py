from django.contrib import admin

from edc_metadata.admin_site import edc_metadata_admin
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .modeladmin_mixins import CrfMetaDataAdminMixin


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(CrfMetaDataAdminMixin, admin.ModelAdmin):

    pass


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(admin.ModelAdmin):
    pass
