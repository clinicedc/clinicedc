from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_visit_schedule_admin
from ..forms import SubjectScheduleHistoryForm
from ..models import SubjectScheduleHistory


@admin.register(SubjectScheduleHistory, site=edc_visit_schedule_admin)
class SubjectScheduleHistoryAdmin(admin.ModelAdmin):

    form = SubjectScheduleHistoryForm

    date_hierarchy = "onschedule_datetime"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "schedule_status",
                    "onschedule_datetime",
                    "offschedule_datetime",
                    "onschedule_model",
                    "offschedule_model",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "visit_schedule_name",
        "schedule_name",
        "schedule_status",
        "onschedule_datetime",
        "offschedule_datetime",
    )

    list_filter = (
        "schedule_status",
        "onschedule_datetime",
        "offschedule_datetime",
        "visit_schedule_name",
        "schedule_name",
    )

    search_fields = ("subject_identifier",)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = (
            fields
            + (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "schedule_status",
                "onschedule_datetime",
                "offschedule_datetime",
                "onschedule_model",
                "offschedule_model",
            )
            + tuple(audit_fieldset_tuple[1].get("fields"))
        )
        return fields
