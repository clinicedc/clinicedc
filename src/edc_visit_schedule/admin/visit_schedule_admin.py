from typing import Tuple

from django.contrib.admin.decorators import register
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_visit_schedule_admin
from ..models import VisitSchedule
from ..site_visit_schedules import site_visit_schedules


@register(VisitSchedule, site=edc_visit_schedule_admin)
class VisitScheduleAdmin(SimpleHistoryAdmin):
    actions = ("populate_visit_schedule",)

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

    search_fields = (
        "visit_schedule_name",
        "schedule_name",
        "visit_code",
        "visit_title",
        "visit_name",
    )

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        return (
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_title",
            "visit_name",
            "timepoint",
            "active",
        ) + list_display

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        return ("active", "visit_schedule_name", "schedule_name", "visit_code") + list_filter

    @staticmethod
    def populate_visit_schedule(request, queryset) -> None:
        VisitSchedule.objects.update(active=False)
        site_visit_schedules.to_model(VisitSchedule)
