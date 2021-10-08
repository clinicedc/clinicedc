from django.contrib.admin.decorators import register
from edc_registration.admin import RegisteredSubjectAdmin as BaseRegisteredSubjectAdmin

from ..admin_site import edc_pharmacy_admin
from ..models import Subject


@register(Subject, site=edc_pharmacy_admin)
class SubjectAdmin(BaseRegisteredSubjectAdmin):
    ordering = ("subject_identifier",)
    search_fields = ("subject_identifier",)
