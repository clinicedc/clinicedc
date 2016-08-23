from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import Panel


class PanelAdmin(BaseModelAdmin):
    list_display = ('name', 'edc_name', 'panel_type')
    filter_horizontal = ("test_code", "aliquot_type", )
    list_filter = ('panel_type', )
admin.site.register(Panel, PanelAdmin)
