from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...forms import ContainerUnitsForm
from ...models import ContainerUnits


@admin.register(ContainerUnits, site=edc_pharmacy_admin)
class ContainerUnitsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = ContainerUnitsForm
