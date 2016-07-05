from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from edc_meta_data.admin import CrfEntryInline, LabEntryInline

from .forms import MembershipFormForm
from .models import MembershipForm, Schedule, VisitDefinition


class EdcVisitScheduleAdminSite(AdminSite):
    site_header = 'Visit Schedule'
    site_title = 'Visit Schedule'
    index_title = 'Visit Schedule Administration'
    site_url = '/edc-visit-schedule/'
edc_visit_schedule_admin = EdcVisitScheduleAdminSite(name='edc_visit_schedule_admin')


@admin.register(MembershipForm, site=edc_visit_schedule_admin)
class MembershipFormAdmin(admin.ModelAdmin):

    form = MembershipFormForm

    list_display = (
        'content_type_map', 'category', 'visible', 'user_created',
        'user_modified', 'created', 'modified')

    list_filter = ('category',)

    search_fields = ('id',)


@admin.register(Schedule, site=edc_visit_schedule_admin)
class ScheduleAdmin(admin.ModelAdmin):

    list_display = ('group_name', 'membership_form', 'grouping_key', 'comment')

    list_filter = ('grouping_key', 'comment')

    search_fields = ('id',)


@admin.register(VisitDefinition, site=edc_visit_schedule_admin)
class VisitDefinitionAdmin(admin.ModelAdmin):

    list_display = ('code', 'title', 'grouping', 'time_point',
                    'base_interval', 'base_interval_unit', 'lower_window',
                    'lower_window_unit', 'upper_window', 'upper_window_unit',
                    'user_modified', 'modified')

    list_filter = ('code', 'grouping', 'time_point', 'base_interval')

    search_fields = ('code', 'grouping', 'id',)

    inlines = [CrfEntryInline, LabEntryInline, ]
