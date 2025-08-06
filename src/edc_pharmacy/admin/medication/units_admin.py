from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...models import Units


@admin.register(Units, site=edc_pharmacy_admin)
class UnitsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
