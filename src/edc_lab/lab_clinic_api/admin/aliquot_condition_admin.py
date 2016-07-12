from django.contrib import admin

from ..models import AliquotCondition


class AliquotConditionAdmin(admin.ModelAdmin):

    list_display = ('display_index', 'name', 'short_name')

admin.site.register(AliquotCondition, AliquotConditionAdmin)
