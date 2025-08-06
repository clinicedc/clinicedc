from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite

from .models import SubjectVisit


class AdminSite(DjangoAdminSite):
    site_title = "Example"
    site_header = "Example"
    index_title = "Example"
    site_url = "/"


edc_dashboard_admin = AdminSite(name="edc_dashboard_admin")


@admin.register(SubjectVisit, site=edc_dashboard_admin)
class SubjectVisitAdmin(admin.ModelAdmin):
    pass
