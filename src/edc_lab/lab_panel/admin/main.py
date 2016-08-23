from django.contrib import admin

from ..models import Panel, PanelGroup, TidPanelMapping


class PanelAdmin(admin.ModelAdmin):

    list_display = ('name', 'panel_group')

    search_fields = ['name', ]

    filter_horizontal = (
        'test_code',
        'aliquot_type')

admin.site.register(Panel, PanelAdmin)


class PanelGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(PanelGroup, PanelGroupAdmin)


class TidPanelMappingAdmin(admin.ModelAdmin):
    list_display = ('tid', 'panel', )
admin.site.register(TidPanelMapping, TidPanelMappingAdmin)
