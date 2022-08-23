from django.contrib import admin
from django.contrib.sites.models import Site
from edc_model_admin.mixins import TemplatesModelAdminMixin

from .admin_site import edc_sites_admin

admin.site.unregister(Site)


@admin.register(Site, site=edc_sites_admin)
class SiteAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    pass
