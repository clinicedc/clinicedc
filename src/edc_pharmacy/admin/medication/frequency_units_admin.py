from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...models import FrequencyUnits


@admin.register(FrequencyUnits, site=edc_pharmacy_admin)
class FrequencyUnitsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
