from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import SubjectIdentifierAuditTrail


class SubjectIdentifierAuditTrailAdmin(BaseModelAdmin):

    list_display = (
        'subject_identifier',
        'date_allocated',
    )
    list_per_page = 15

admin.site.register(SubjectIdentifierAuditTrail, SubjectIdentifierAuditTrailAdmin)
