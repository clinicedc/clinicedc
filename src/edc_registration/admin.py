from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_sites.site import sites

from .admin_site import edc_registration_admin
from .modeladmin_mixins import RegisteredSubjectModelAdminMixin
from .utils import get_registered_subject_model_cls


@admin.register(get_registered_subject_model_cls(), site=edc_registration_admin)
class RegisteredSubjectAdmin(
    SiteModelAdminMixin, RegisteredSubjectModelAdminMixin, SimpleHistoryAdmin
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

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        if request.user.userprofile.roles.filter(name=DATA_MANAGER_ROLE).exists():
            return [
                s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id
            ]
        return sites.get_view_only_site_ids_for_user(request=request)
