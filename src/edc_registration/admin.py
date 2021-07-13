from django.contrib import admin
from edc_model_admin import SimpleHistoryAdmin, audit_fieldset_tuple

from .admin_site import edc_registration_admin
from .modeladmin_mixins import RegisteredSubjectModelAdminMixin
from .utils import get_registered_subject_model_cls


@admin.register(get_registered_subject_model_cls(), site=edc_registration_admin)
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
