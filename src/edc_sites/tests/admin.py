from django.contrib import admin
from django.contrib.admin import ModelAdmin

from edc_sites.admin import SiteModelAdminMixin
from edc_sites.tests.models import TestModelWithSite


@admin.register(TestModelWithSite)
class TestModelWithSiteAdmin(SiteModelAdminMixin, ModelAdmin):
    pass
