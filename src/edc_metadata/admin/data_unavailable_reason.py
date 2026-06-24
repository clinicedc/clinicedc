from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ..admin_site import edc_metadata_admin
from ..models import DataUnavailableReason


@admin.register(DataUnavailableReason, site=edc_metadata_admin)
class DataUnavailableReasonAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
