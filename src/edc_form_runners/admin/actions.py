from django.contrib import admin
from edc_constants.constants import DONE, IN_PROGRESS, NEW

from ..single_form_runner import SingleFormRunner


@admin.action(description="Refresh selected issues")
def issue_refresh(modeladmin, request, queryset):
    for obj in queryset:
        runner = SingleFormRunner(issue_obj=obj)
        runner.run()


@admin.action(description="Mark selected issues as done")
def issue_flag_as_done(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = DONE
        obj.save()


@admin.action(description="Mark selected issues as in progress")
def issue_flag_as_in_progress(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = IN_PROGRESS
        obj.save()


@admin.action(description="Mark selected issues as new")
def issue_flag_as_new(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = NEW
        obj.save()
