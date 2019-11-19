from django.contrib import admin

from ..admin_site import edc_metadata_admin
from ..modeladmin_mixins import CrfMetadataAdminMixin
from ..models import CrfMetadata


@admin.register(CrfMetadata, site=edc_metadata_admin)
class CrfMetadataAdmin(CrfMetadataAdminMixin, admin.ModelAdmin):

    pass
