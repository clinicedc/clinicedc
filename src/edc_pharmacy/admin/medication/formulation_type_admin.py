from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...models import FormulationType


@admin.register(FormulationType, site=edc_pharmacy_admin)
class FormulationTypeAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
