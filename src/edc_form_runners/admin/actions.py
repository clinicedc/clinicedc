from django.contrib import admin

from ..get_form_runner_by_src_id import get_form_runner_by_src_id


@admin.action(description="Refresh selected issues")
def issue_refresh(modeladmin, request, queryset):
    for issue_obj in queryset:
        runner = get_form_runner_by_src_id(
            src_id=issue_obj.src_id, model_name=issue_obj.label_lower
        )
        runner.run_one()
