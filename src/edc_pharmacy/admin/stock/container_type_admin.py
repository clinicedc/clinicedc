from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...forms import ContainerTypeForm
from ...models import ContainerType


@admin.register(ContainerType, site=edc_pharmacy_admin)
class ContainerTypeAdmin(ListModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = ContainerTypeForm
