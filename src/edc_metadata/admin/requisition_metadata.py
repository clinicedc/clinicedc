from django.contrib import admin

from ..admin_site import edc_metadata_admin
from ..modeladmin_mixins import RequisitionMetadataAdminMixin
from ..models import RequisitionMetadata


@admin.register(RequisitionMetadata, site=edc_metadata_admin)
class RequisitionMetadataAdmin(RequisitionMetadataAdminMixin, admin.ModelAdmin):
    pass
