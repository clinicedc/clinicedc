from django.contrib import admin
from edc_model_admin import audit_fields
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin


class RegisteredSubjectModelAdminMixin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):

    date_hierarchy = "registration_datetime"

    instructions = []

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
            ] + list(audit_fields)
        )

    def get_list_display(self, request):
        return [
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
        ] + list(super().get_list_display(request))

    def get_list_filter(self, request):
        return [
            "subject_type",
            "registration_status",
            "screening_datetime",
            "registration_datetime",
            "gender",
            "site",
            "hostname_created",
        ] + list(super().get_list_filter(request))

    def get_search_fields(self, request):
        return [
            "subject_identifier",
            "first_name",
            "initials",
            "sid",
            "identity",
            "id",
            "screening_identifier",
            "registration_identifier",
        ] + list(super().get_search_fields(request))
