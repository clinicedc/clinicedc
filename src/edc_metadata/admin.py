from django.contrib import admin

from .admin_site import edc_metadata_admin
from .modeladmin_mixins import CrfMetaDataAdminMixin
from .models import CrfMetadata, RequisitionMetadata


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(CrfMetaDataAdminMixin, admin.ModelAdmin):

    pass


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(admin.ModelAdmin):
    pass
