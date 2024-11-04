from django.contrib import admin

from ...admin_site import edc_pharmacy_admin
from ...models import SiteProxy


@admin.register(SiteProxy, site=edc_pharmacy_admin)
class SiteProxyAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
