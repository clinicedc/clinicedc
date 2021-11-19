from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from edc_registration.admin import RegisteredSubjectAdmin as BaseRegisteredSubjectAdmin

from ..admin_site import edc_pharmacy_admin
from ..models import Subject, VisitSchedule


@register(Subject, site=edc_pharmacy_admin)
class SubjectAdmin(BaseRegisteredSubjectAdmin):
    ordering = ("subject_identifier",)
    search_fields = ("subject_identifier",)


@register(VisitSchedule, site=edc_pharmacy_admin)
class VisitScheduleAdmin(ModelAdmin):
    ordering = ("visit_schedule_name", "schedule_name", "visit_code")
    search_fields = ("visit_code", "visit_title")
