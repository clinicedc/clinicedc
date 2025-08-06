from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from ...admin_site import edc_pharmacy_admin
from ...models import Route


@admin.register(Route, site=edc_pharmacy_admin)
class RouteAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
