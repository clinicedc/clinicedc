import re

from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields.admin import audit_fields

from edc_auth.constants import PII, PII_VIEW
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_protocol.research_protocol_config import ResearchProtocolConfig


class RegisteredSubjectModelAdminMixin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    name_display_fields: tuple[str] = ("first_name", "last_name")

    ordering = ("registration_datetime",)

    date_hierarchy = "registration_datetime"

    instructions = ()

    change_list_note = format_html(
        "If <strong>sensitive data</strong> is available and the user has permissions "
        "to view, the <strong>sensitive data</strong> will only show for a search result "
        "that is an exact match for a given <strong>Subject ID</strong>. If multiple results "
        "appear, click on a <strong>Subject ID</strong> to add it to the search filter.",
        "",
    )

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
            return self.fieldsets_no_pii
        return [(None, {"fields": self.get_fields(request, obj)})]

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return (
            *readonly_fields,
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
            *audit_fields,
        )

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        pii_fields = [*self.name_display_fields, "initials", "identity"]
        list_display = [col for col in list_display if col not in pii_fields]
        has_perms_for_pii = request.user.groups.filter(name=PII).exists()
        MASK = "*****"  # noqa: N806

        pattern = ResearchProtocolConfig().subject_identifier_pattern
        query = request.GET.get("q", "").strip()
        search_active = re.match(pattern, query)

        @admin.display(description="Edit/View")
        def edit(obj) -> str:
            return "Edit"

        @admin.display(description="Subject ID")
        def subject_identifier_link(obj) -> str:
            return format_html(
                '<A title="search on this subject ID" href="?q={}">{}</A>',
                obj.subject_identifier,
                obj.subject_identifier,
            )

        @admin.display(description="Initials")
        def masked_initials(obj) -> str:
            return obj.initials if has_perms_for_pii else MASK

        @admin.display(description="Name")
        def masked_full_name(obj) -> str:
            name = [
                getattr(obj, s) if has_perms_for_pii and search_active else MASK
                for s in self.name_display_fields
            ]
            return " ".join(name)

        custom_fields = (
            edit,
            subject_identifier_link,
            "dashboard",
            masked_full_name,
            masked_initials,
            "gender",
            "subject_type",
            "screening_identifier",
            "sid",
            "registration_status",
            "site",
            "user_created",
            "created",
        )
        return *custom_fields, *[f for f in list_display if f not in custom_fields]

    def get_list_filter(self, request) -> tuple[str, ...]:
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
        return *custom_fields, *[f for f in list_filter if f not in custom_fields]

    def get_search_fields(self, request) -> tuple[str, ...]:
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
