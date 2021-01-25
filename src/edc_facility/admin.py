from django.contrib import admin

from .admin_site import edc_facility_admin
from .models import Holiday


@admin.register(Holiday, site=edc_facility_admin)
class HolidayAdmin(admin.ModelAdmin):

    date_hierarchy = "local_date"
    list_display = ("name", "local_date")
