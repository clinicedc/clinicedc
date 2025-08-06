from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite

from .models import SubjectVisit


class AdminSite(DjangoAdminSite):
    site_title = "edc_listboard"
    site_header = "edc_listboard"
    index_title = "edc_listboard"
    site_url = "/"


edc_listboard_admin = AdminSite(name="edc_listboard_admin")


@admin.register(SubjectVisit, site=edc_listboard_admin)
class SubjectVisitAdmin(admin.ModelAdmin):
    pass
