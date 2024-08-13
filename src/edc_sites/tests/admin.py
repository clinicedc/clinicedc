from django.contrib import admin
from django.contrib.admin import ModelAdmin

from edc_sites.admin import SiteModelAdminMixin

from .models import TestModelWithSite


@admin.register(TestModelWithSite)
class TestModelWithSiteAdmin(SiteModelAdminMixin, ModelAdmin):
    pass
