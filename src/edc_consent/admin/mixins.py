from django.contrib import admin

from edc_consent.actions import flag_as_verified_against_paper, unflag_as_verified_against_paper


class ModelAdminConsentMixin(object):

    remove_consent_fields = []

    search_fields = ['id', 'subject_identifier', 'first_name', 'last_name', 'identity']

    actions = [flag_as_verified_against_paper, unflag_as_verified_against_paper]

    consent_fields = [
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

    consent_radio_fields = {
        "language": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "is_dob_estimated": admin.VERTICAL,
        "identity_type": admin.VERTICAL,
        "is_incarcerated": admin.VERTICAL,
        "may_store_samples": admin.VERTICAL,
        "consent_reviewed": admin.VERTICAL,
        "study_questions": admin.VERTICAL,
        "assessment_score": admin.VERTICAL,
        "consent_copy": admin.VERTICAL,
        "is_literate": admin.VERTICAL}

    def get_fields(self, request, obj=None):
        if self.consent_fields:
            self.fields = self.remove_fields_from(self.consent_fields)
            self.radio_fields = self.remove_radio_fields()
            return self.fields
        elif self.fields:
            return self.fields
        form = self.get_form(request, obj, fields=None)
        return list(form.base_fields) + list(self.get_readonly_fields(request, obj))

    def remove_radio_fields(self):
        for key in self.remove_consent_fields:
            try:
                del self.consent_radio_fields[key]
            except KeyError:
                pass
        return self.consent_radio_fields

    def remove_fields_from(self, field_list):
        field_list = list(field_list)
        for field in self.remove_consent_fields:
            try:
                field_list.remove(field)
            except ValueError:
                pass
        return tuple(field_list)

    def get_list_display(self, request):
        self.list_display = list(super(ModelAdminConsentMixin, self).get_list_display(request) or [])
        self.list_display = self.list_display + [
            'subject_identifier', 'is_verified', 'is_verified_datetime', 'first_name',
            'initials', 'gender', 'dob', 'may_store_samples', 'consent_datetime', 'created', 'modified',
            'user_created', 'user_modified']
        self.list_display = self.remove_fields_from(self.list_display)
        return tuple(self.list_display)

    def get_list_filter(self, request):
        self.list_filter = list(super(ModelAdminConsentMixin, self).get_list_filter(request) or [])
        self.list_filter = self.list_filter + [
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
        self.list_filter = self.remove_fields_from(self.list_filter)
        return tuple(self.list_filter)

    def get_readonly_fields(self, request, obj=None):
        super(ModelAdminConsentMixin, self).get_readonly_fields(request, obj)
        if obj:
            return (
                'subject_identifier',
                'subject_identifier_as_pk',
                'study_site',
                'consent_datetime',) + self.readonly_fields
        else:
            return ('subject_identifier', 'subject_identifier_as_pk',) + self.readonly_fields
