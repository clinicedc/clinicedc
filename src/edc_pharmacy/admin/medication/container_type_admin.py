from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...models import ContainerType


@admin.register(ContainerType, site=edc_pharmacy_admin)
class ContainerTypeAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
