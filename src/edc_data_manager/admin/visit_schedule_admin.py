from django_audit_fields.admin import audit_fieldset_tuple
from django.contrib.admin.decorators import register
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import edc_data_manager_admin
from ..models import VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@register(VisitSchedule, site=edc_data_manager_admin)
class VisitScheduleAdmin(SimpleHistoryAdmin):

    actions = ["populate_visit_schedule"]

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_name",
                    "timepoint",
                    "active",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "visit_schedule_name",
        "schedule_name",
        "visit_code",
        "visit_name",
        "timepoint",
        "active",
    )

    list_filter = ("active", "visit_schedule_name", "schedule_name", "visit_code")

    search_fields = ("visit_schedule_name", "schedule_name", "visit_code", "visit_name")

    def populate_visit_schedule(self, request, queryset):
        VisitSchedule.objects.update(active=False)
        site_visit_schedules.to_model(VisitSchedule)
