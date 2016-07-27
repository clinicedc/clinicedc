from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from .models import Holiday


class EdcAppointmentAdminSite(AdminSite):
    site_header = 'Appointments'
    site_title = 'Appointments'
    index_title = 'Appointments Administration'
    site_url = '/'
edc_appointment_admin = EdcAppointmentAdminSite(name='edc_appointment_admin')


@admin.register(Holiday, site=edc_appointment_admin)
class HolidayAdmin(admin.ModelAdmin):
    pass


class HolidayInlineAdmin(admin.TabularInline):
    model = Holiday
    extra = 0
