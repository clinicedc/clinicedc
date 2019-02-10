from django.contrib import admin
from edc_consent.actions import (
    flag_as_verified_against_paper,
    unflag_as_verified_against_paper,
)
from edc_model_admin import ModelAdminBasicMixin


class ModelAdminConsentMixin(ModelAdminBasicMixin):

    actions = [flag_as_verified_against_paper, unflag_as_verified_against_paper]

    def get_readonly_fields(self, request, obj=None):
        super(ModelAdminConsentMixin, self).get_readonly_fields(request, obj)
        if obj:
            return (
                "subject_identifier",
                "subject_identifier_as_pk",
                "consent_datetime",
            ) + self.readonly_fields
        else:
            return (
                "subject_identifier",
                "subject_identifier_as_pk",
            ) + self.readonly_fields

    mixin_search_fields = [
        "id",
        "subject_identifier",
        "first_name",
        "last_name",
        "identity",
    ]

    mixin_fields = [
        "subject_identifier",
        "first_name",
        "last_name",
        "initials",
        "language",
        "is_literate",
        "witness_name",
        "consent_datetime",
        "gender",
        "dob",
        "guardian_name",
        "is_dob_estimated",
        "identity",
        "identity_type",
        "confirm_identity",
        "is_incarcerated",
        "may_store_samples",
        "comment",
        "consent_reviewed",
        "study_questions",
        "assessment_score",
        "consent_copy",
    ]

    mixin_radio_fields = {
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
        "is_literate": admin.VERTICAL,
    }

    mixin_list_display = [
        "subject_identifier",
        "is_verified",
        "is_verified_datetime",
        "first_name",
        "initials",
        "gender",
        "dob",
        "may_store_samples",
        "consent_datetime",
        "created",
        "modified",
        "user_created",
        "user_modified",
    ]

    mixin_list_filter = [
        "gender",
        "is_verified",
        "is_verified_datetime",
        "language",
        "may_store_samples",
        "is_literate",
        "consent_datetime",
        "created",
        "modified",
        "user_created",
        "user_modified",
        "hostname_created",
    ]
