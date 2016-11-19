from django.contrib import admin

from .admin_site import edc_appointment_admin

from .models import Holiday


@admin.register(Holiday, site=edc_appointment_admin)
class HolidayAdmin(admin.ModelAdmin):

    date_hierarchy = 'day'
    list_display = ('name', 'day', )
