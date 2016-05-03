from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from .actions import flag_as_verified_against_paper, unflag_as_verified_against_paper
from .models import ConsentType


class ConsentTypeAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_datetime'
    fields = ('app_label', 'model_name', 'version', 'start_datetime', 'end_datetime')
    list_display = ('app_label', 'model_name', 'version', 'start_datetime', 'end_datetime')
    list_filter = ('version', 'start_datetime', 'end_datetime')
admin.site.register(ConsentType, ConsentTypeAdmin)


class BaseConsentModelAdmin(BaseModelAdmin):
    list_display = [
        'subject_identifier', 'is_verified', 'is_verified_datetime', 'first_name',
        'initials', 'gender', 'dob', 'consent_datetime', 'created', 'modified',
        'user_created', 'user_modified']
    search_fields = ['id', 'subject_identifier', 'first_name', 'last_name', 'identity']
    actions = [flag_as_verified_against_paper, unflag_as_verified_against_paper]
    list_filter = [
        'gender',
        'is_verified',
        'is_verified_datetime',
        'language',
        'may_store_samples',
        'study_site',
        'is_literate',
        'consent_datetime',
        'created',
        'modified',
        'user_created',
        'user_modified',
        'hostname_created']
    fields = [
        'subject_identifier',
        'first_name',
        'last_name',
        'initials',
        'language',
        'is_literate',
        'witness_name',
        'consent_datetime',
        'study_site',
        'gender',
        'dob',
        'guardian_name',
        'is_dob_estimated',
        'identity',
        'identity_type',
        'confirm_identity',
        'is_incarcerated',
        'may_store_samples',
        'comment',
        'consent_reviewed',
        'study_questions',
        'assessment_score',
        'consent_copy']

    radio_fields = {
        "language": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "study_site": admin.VERTICAL,
        "is_dob_estimated": admin.VERTICAL,
        "identity_type": admin.VERTICAL,
        "is_incarcerated": admin.VERTICAL,
        "may_store_samples": admin.VERTICAL,
        "consent_reviewed": admin.VERTICAL,
        "study_questions": admin.VERTICAL,
        "assessment_score": admin.VERTICAL,
        "consent_copy": admin.VERTICAL,
        "is_literate": admin.VERTICAL}

    # override to disallow subject to be changed
    def get_readonly_fields(self, request, obj=None):
        super(BaseConsentModelAdmin, self).get_readonly_fields(request, obj)
        if obj:  # In edit mode
            return (
                'subject_identifier',
                'subject_identifier_as_pk',
                'study_site',
                'consent_datetime',) + self.readonly_fields
        else:
            return ('subject_identifier', 'subject_identifier_as_pk',) + self.readonly_fields
