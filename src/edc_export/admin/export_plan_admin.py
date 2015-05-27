from django.contrib import admin

from ..models import ExportPlan


class ExportPlanAdmin (admin.ModelAdmin):

    list_display = ('app_label', 'object_name',)
    list_filter = ('app_label', 'object_name', )

admin.site.register(ExportPlan, ExportPlanAdmin)
