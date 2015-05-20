from django.contrib import admin
from edc.base.modeladmin.admin import BaseModelAdmin
from ..models import ScheduleGroup


class ScheduleGroupAdmin(BaseModelAdmin):

    list_display = ('group_name', 'membership_form', 'grouping_key', 'comment')

    list_filter = ('grouping_key', 'comment')

    search_fields = ('id',)


admin.site.register(ScheduleGroup, ScheduleGroupAdmin)
