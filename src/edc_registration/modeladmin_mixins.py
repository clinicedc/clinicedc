from django.contrib import admin
from edc_auth import PII_VIEW, PII
from edc_model_admin import audit_fields
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin


class RegisteredSubjectModelAdminMixin(
    ModelAdminSubjectDashboardMixin, admin.ModelAdmin
):

    ordering = ("registration_datetime",)

    date_hierarchy = "registration_datetime"

    instructions = []

    def show_pii(self, request):
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            list(readonly_fields)
            + [
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
            ]
            + list(audit_fields)
        )

    def get_list_display(self, request):

        if self.show_pii(request):
            list_display = [
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
            ]
        else:
            list_display = [
                "subject_identifier",
                "dashboard",
                "gender",
                "subject_type",
                "sid",
                "registration_status",
                "site",
                "user_created",
                "created",
            ]
        return list_display + list(super().get_list_display(request))

    def get_list_filter(self, request):
        super().get_list_filter(request)
        if self.show_pii(request):
            fields = [
                "subject_type",
                "registration_status",
                "screening_datetime",
                "registration_datetime",
                "gender",
                "site",
                "hostname_created",
            ]
        else:
            fields = [
                "subject_type",
                "registration_status",
                "screening_datetime",
                "registration_datetime",
                "site",
                "hostname_created",
            ]
        self.list_filter = [f for f in fields if f not in self.list_filter] + list(
            self.list_filter
        )
        return self.list_filter

    def get_search_fields(self, request):
        if self.show_pii(request):
            search_fields = [
                "subject_identifier",
                "first_name",
                "initials",
                "sid",
                "identity",
                "id",
                "screening_identifier",
                "registration_identifier",
            ]
        else:
            search_fields = [
                "subject_identifier",
                "sid",
                "id",
                "screening_identifier",
                "registration_identifier",
            ]
        return search_fields + list(super().get_search_fields(request))
