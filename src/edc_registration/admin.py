from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_data_manager.modeladmin_mixins import DataManagerSiteModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin

from .admin_site import edc_registration_admin
from .modeladmin_mixins import RegisteredSubjectModelAdminMixin
from .utils import get_registered_subject_model_cls


@admin.register(get_registered_subject_model_cls(), site=edc_registration_admin)
class RegisteredSubjectAdmin(
    DataManagerSiteModelAdminMixin, RegisteredSubjectModelAdminMixin, SimpleHistoryAdmin
):
    ordering = ("subject_identifier",)

    fieldsets = (
        (
            "Subject",
            {
                "fields": (
                    "subject_identifier",
                    "sid",
                    "subject_type",
                    "registration_status",
                    "registration_datetime",
                )
            },
        ),
        (
            "Personal Details",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "initials",
                    "dob",
                    "gender",
                    "identity",
                )
            },
        ),
        (
            "Screening Details",
            {
                "fields": (
                    "screening_identifier",
                    "screening_datetime",
                )
            },
        ),
        (
            "Consent Details",
            {"fields": ("consent_datetime", "subject_consent_id")},
        ),
        (
            "Registration Details",
            {
                "fields": (
                    "randomization_list_model",
                    "randomization_datetime",
                    # "sid",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    fieldsets_no_pii = (
        (
            "Subject",
            {
                "fields": (
                    "subject_identifier",
                    "sid",
                    "subject_type",
                    "registration_status",
                    "registration_datetime",
                )
            },
        ),
        ("Personal Details", {"fields": ("gender",)}),
        (
            "Registration Details",
            {
                "fields": (
                    "screening_identifier",
                    "screening_datetime",
                    "randomization_datetime",
                    "consent_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )
