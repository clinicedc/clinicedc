from django.contrib import admin

from edc_consent.models import ConsentType


class ConsentTypeAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_datetime'
    fields = ('app_label', 'model_name', 'version', 'start_datetime', 'end_datetime')
    list_display = ('app_label', 'model_name', 'version', 'start_datetime', 'end_datetime')
    list_filter = ('version', 'start_datetime', 'end_datetime')
admin.site.register(ConsentType, ConsentTypeAdmin)
