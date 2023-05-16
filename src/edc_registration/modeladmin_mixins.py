from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fields
from edc_auth.auth_objects import PII, PII_VIEW
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin


class RegisteredSubjectModelAdminMixin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    ordering = ("registration_datetime",)

    date_hierarchy = "registration_datetime"

    instructions = []

    @staticmethod
    def show_pii(request) -> bool:
        return request.user.groups.filter(name__in=[PII, PII_VIEW]).exists()

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets.
        """
        if self.fieldsets:
            if self.show_pii(request):
                return self.fieldsets
            else:
                return self.fieldsets_no_pii
        return [(None, {"fields": self.get_fields(request, obj)})]

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            readonly_fields
            + (
                "subject_identifier",
                "sid",
                "first_name",
                "last_name",
                "initials",
                "dob",
                "gender",
                "subject_type",
                "registration_status",
                "identity",
                "screening_identifier",
                "screening_datetime",
                "registration_datetime",
                "randomization_datetime",
                "consent_datetime",
            )
            + audit_fields
        )

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if self.show_pii(request):
            custom_fields = (
                "subject_identifier",
                "dashboard",
                "first_name",
                "initials",
                "gender",
                "subject_type",
                "sid",
                "registration_status",
                "site",
                "user_created",
                "created",
            )
        else:
            custom_fields = (
                "subject_identifier",
                "dashboard",
                "gender",
                "subject_type",
                "sid",
                "registration_status",
                "site",
                "user_created",
                "created",
            )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            "subject_type",
            "registration_status",
            "screening_datetime",
            "registration_datetime",
            "gender",
            "site",
            "hostname_created",
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        pii_fields = (
            "first_name",
            "initials",
            "identity",
        )
        search_fields += (
            "subject_identifier",
            "sid",
            "id",
            "screening_identifier",
            "registration_identifier",
        )
        if not self.show_pii(request):
            return tuple(set(f for f in search_fields if f not in pii_fields))
        return tuple(set(search_fields + pii_fields))
