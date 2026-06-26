from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_metadata_admin
from ...models import DataMissingReason


@admin.register(DataMissingReason, site=edc_metadata_admin)
class DataMissingReasonAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
