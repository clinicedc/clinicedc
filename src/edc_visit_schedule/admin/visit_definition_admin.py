from django.contrib import admin

from edc.base.modeladmin.admin import BaseModelAdmin
from edc.subject.entry.admin import EntryInline, LabEntryInline

from ..actions import export_as_html
from ..models import VisitDefinition


class VisitDefinitionAdmin(BaseModelAdmin):

    list_display = ('code', 'title', 'grouping', 'time_point', 'base_interval', 'base_interval_unit', 'lower_window', 'lower_window_unit', 'upper_window', 'upper_window_unit', 'user_modified', 'modified')

    list_filter = ('code', 'grouping', 'time_point', 'base_interval')

    search_fields = ('code', 'grouping', 'id',)

    inlines = [EntryInline, LabEntryInline, ]

    actions = [export_as_html, ]
admin.site.register(VisitDefinition, VisitDefinitionAdmin)
