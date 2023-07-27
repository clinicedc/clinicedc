from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from .admin_site import edc_facility_admin
from .modeladmin_mixins import HealthFacilityModelAdminMixin
from .models import HealthFacility, HealthFacilityTypes, Holiday


@admin.register(Holiday, site=edc_facility_admin)
class HolidayAdmin(admin.ModelAdmin):
    date_hierarchy = "local_date"
    list_display = ("name", "local_date")


@admin.register(HealthFacility, site=edc_facility_admin)
class HealthFacilityAdmin(HealthFacilityModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(HealthFacilityTypes, site=edc_facility_admin)
class HealthFacilityTypesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
