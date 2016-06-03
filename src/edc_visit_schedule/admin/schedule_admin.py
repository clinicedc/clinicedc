from django.contrib import admin

from .base_model_admin import BaseModelAdmin

from ..models import Schedule


class ScheduleAdmin(BaseModelAdmin):

    list_display = ('group_name', 'membership_form', 'grouping_key', 'comment')

    list_filter = ('grouping_key', 'comment')

    search_fields = ('id',)


admin.site.register(Schedule, ScheduleAdmin)
