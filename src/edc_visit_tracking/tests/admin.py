from django.contrib import admin

from ..admin_site import edc_visit_tracking_admin
from .models import SubjectVisit


@admin.register(SubjectVisit, site=edc_visit_tracking_admin)
class SubjectVisitAdmin(admin.ModelAdmin):
    pass
