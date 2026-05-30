from django.contrib import admin
from django.contrib.admin.decorators import register

from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_visit_schedule_admin
from ..models import VisitScheduleSummary


@register(VisitScheduleSummary, site=edc_visit_schedule_admin)
class VisitScheduleSummaryAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    fieldsets = (
        [
            None,
            {"fields": ("visit_schedule_name", "schedule_name", "label")},
        ],
    )

    list_display = ("label", "visit_schedule_name", "schedule_name")

    list_filter = ("label",)

    search_fields = ("visit_schedule_name", "schedule_name", "label")

    readonly_fields = ("visit_schedule_name", "schedule_name", "label")
