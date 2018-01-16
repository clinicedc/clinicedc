from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple, audit_fields

from .admin_mixins import RegisteredSubjectModelAdminMixin
from .admin_site import edc_registration_admin
from .models import RegisteredSubject


@admin.register(RegisteredSubject, site=edc_registration_admin)
class RegisteredSubjectAdmin(RegisteredSubjectModelAdminMixin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'sid', 'first_name', 'last_name', 'initials', 'dob', 'gender',
                'subject_type', 'registration_status', 'identity', 'screening_identifier',
                'screening_datetime', 'registration_datetime',
                'randomization_datetime', 'consent_datetime')}),
        audit_fieldset_tuple
    )

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + (
            'subject_identifier',
            'sid', 'first_name', 'last_name', 'initials', 'dob', 'gender',
            'subject_type', 'registration_status', 'identity', 'screening_identifier',
            'screening_datetime', 'registration_datetime',
            'randomization_datetime', 'consent_datetime') + audit_fields
        return fields
