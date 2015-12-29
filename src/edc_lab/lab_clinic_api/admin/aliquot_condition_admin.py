from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import AliquotCondition


class AliquotConditionAdmin(BaseModelAdmin):
    list_display = ('display_index', 'name', 'short_name')
admin.site.register(AliquotCondition, AliquotConditionAdmin)
