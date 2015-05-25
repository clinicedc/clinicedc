from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..forms import RegisteredSubjectForm
from ..models import RegisteredSubject


class RegisteredSubjectAdmin (BaseModelAdmin):

    form = RegisteredSubjectForm
    date_hierarchy = 'registration_datetime'

    list_display = (
        'subject_identifier',
        'dashboard',
        'first_name',
        'initials',
        'gender',
        'subject_type',
        'sid',
        'registration_status',
        'study_site',
        'user_created',
        'created',
    )

    readonly_fields = (
        'subject_identifier',
        'subject_identifier_as_pk',
    )

    search_fields = (
        'subject_identifier', 'first_name', 'initials', 'sid', 'identity', 'id', 'registration_identifier')

    list_filter = ('subject_type', 'registration_status', 'registration_datetime', 'gender',
                   'study_site', 'hiv_status', 'survival_status', 'may_store_samples', 'hostname_created')

admin.site.register(RegisteredSubject, RegisteredSubjectAdmin)
