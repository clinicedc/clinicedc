from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple, SimpleHistoryAdmin

from .admin_site import edc_registration_admin
from .modeladmin_mixins import RegisteredSubjectModelAdminMixin
from .models import RegisteredSubject


@admin.register(RegisteredSubject, site=edc_registration_admin)
class RegisteredSubjectAdmin(RegisteredSubjectModelAdminMixin, SimpleHistoryAdmin):

    ordering = ("subject_identifier",)

    fieldsets = (
        ("Subject", {"fields": ("subject_identifier", "sid", "subject_type")}),
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
            "Registration Details",
            {
                "fields": (
                    "registration_status",
                    "screening_identifier",
                    "screening_datetime",
                    "registration_datetime",
                    "randomization_datetime",
                    "consent_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    fieldsets_no_pii = (
        ("Subject", {"fields": ("subject_identifier", "sid", "subject_type")}),
        ("Personal Details", {"fields": ("gender",)}),
        (
            "Registration Details",
            {
                "fields": (
                    "registration_status",
                    "screening_identifier",
                    "screening_datetime",
                    "registration_datetime",
                    "randomization_datetime",
                    "consent_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )
