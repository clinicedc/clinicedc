from django.contrib import admin

from .base_model_admin import BaseModelAdmin

from ..models import AliquotCondition


class AliquotConditionAdmin(BaseModelAdmin):

    list_display = ('display_index', 'name', 'short_name')

admin.site.register(AliquotCondition, AliquotConditionAdmin)
