from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin
from edc_meta_data.admin import CrfEntryInline, LabEntryInline

from ..models import VisitDefinition


class VisitDefinitionAdmin(BaseModelAdmin):

    list_display = ('code', 'title', 'grouping', 'time_point',
                    'base_interval', 'base_interval_unit', 'lower_window',
                    'lower_window_unit', 'upper_window', 'upper_window_unit',
                    'user_modified', 'modified')

    list_filter = ('code', 'grouping', 'time_point', 'base_interval')

    search_fields = ('code', 'grouping', 'id',)

    inlines = [CrfEntryInline, LabEntryInline, ]

admin.site.register(VisitDefinition, VisitDefinitionAdmin)
