from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register

from ..admin_site import edc_pharmacy_admin
from ..models import SiteProxy, VisitSchedule


@register(VisitSchedule, site=edc_pharmacy_admin)
class VisitScheduleAdmin(ModelAdmin):
    ordering = ("visit_schedule_name", "schedule_name", "visit_code")
    search_fields = ("visit_code", "visit_title")


@register(SiteProxy, site=edc_pharmacy_admin)
class SiteProxyAdmin(ModelAdmin):
    ordering = ("name",)
    search_fields = ["id", "name"]
