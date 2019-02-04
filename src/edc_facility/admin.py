from django.contrib import admin

from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):

    date_hierarchy = "local_date"
    list_display = ("name", "local_date")
