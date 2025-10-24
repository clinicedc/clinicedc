from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_dashboard.url_names import url_names
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import ModelAdminHideDeleteButtonOnCondition
from edc_screening.screening_eligibility import ScreeningEligibility
from edc_sites.admin import SiteModelAdminMixin
from edc_utils import get_uuid

from .admin_site import demo_screening_admin
from .models import SubjectScreening


@admin.register(SubjectScreening, site=demo_screening_admin)
class SubjectScreeningAdmin(
    ModelAdminSubjectDashboardMixin,
    ModelAdminHideDeleteButtonOnCondition,
    SiteModelAdminMixin,
    SimpleHistoryAdmin,
):
    # form = SubjectScreeningForm

    post_url_on_delete_name = "screening_listboard_url"  # url_name

    skip_auto_numbering = ("safe_save_id",)

    additional_instructions = (
        "Patients must meet ALL of the inclusion criteria and NONE of the "
        "exclusion criteria in order to be considered eligible for enrolment"
    )

    fieldsets = (
        [
            None,
            {
                "fields": ("screening_identifier", "report_datetime", "site"),
            },
        ],
        [
            "Demographics",
            {
                "fields": (
                    "initials",
                    "gender",
                    "age_in_years",
                )
            },
        ],
        [
            "Additional Criteria",
            {
                "fields": (
                    "willing_to_participate",
                    "consent_ability",
                ),
            },
        ],
        [
            "Additional Comments",
            {
                "fields": (
                    "unsuitable_for_study",
                    "unsuitable_reason",
                    "unsuitable_reason_other",
                    "unsuitable_agreed",
                ),
            },
        ],
        [
            "Eligibility",
            {
                "classes": ("collapse",),
                "fields": (
                    "subject_identifier",
                    "eligible",
                    "eligibility_datetime",
                    "real_eligibility_datetime",
                    "reasons_ineligible",
                    "consented",
                    "refused",
                ),
            },
        ],
        [
            audit_fieldset_tuple[0],
            {
                "classes": audit_fieldset_tuple[1]["classes"],
                "fields": (*audit_fieldset_tuple[1]["fields"], "safe_save_id"),
            },
        ],
    )

    radio_fields = {  # noqa: RUF012
        "consent_ability": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "unsuitable_agreed": admin.VERTICAL,
        "unsuitable_for_study": admin.VERTICAL,
        "unsuitable_reason": admin.VERTICAL,
        "willing_to_participate": admin.VERTICAL,
    }

    list_display = (
        "screening_identifier",
        "eligibility_status",
        "demographics",
        "reasons",
        "report_datetime",
        "user_created",
        "created",
    )

    list_filter = (
        "report_datetime",
        "gender",
        "eligible",
        "unsuitable_for_study",
        "consented",
        "refused",
    )

    search_fields = (
        "screening_identifier",
        "subject_identifier",
        "initials",
        "reasons_ineligible",
    )

    readonly_fields = (
        "screening_identifier",
        "subject_identifier",
        "eligible",
        "eligibility_datetime",
        "real_eligibility_datetime",
        "reasons_ineligible",
        "consented",
        "refused",
    )

    def get_post_url_on_delete_name(self, request) -> str:
        return url_names.get(self.post_url_on_delete_name)

    def post_url_on_delete_kwargs(self, request, obj):
        return {}

    @staticmethod
    def demographics(obj=None):
        return format_html(
            "{} {}yrs<BR>Initials: {}<BR><BR>",
            obj.get_gender_display(),
            obj.age_in_years,
            obj.initials.upper(),
        )

    @staticmethod
    def reasons(obj=None):
        eligibility = ScreeningEligibility(obj)
        return mark_safe(  # noqa: S308
            conditional_escape(eligibility.formatted_reasons_ineligible())
        )

    @staticmethod
    def eligibility_status(obj=None):
        eligibility = ScreeningEligibility(obj)
        return mark_safe(conditional_escape(eligibility.display_label))  # noqa: S308

    def hide_delete_button_on_condition(self, request, object_id) -> bool:
        try:
            obj = SubjectScreening.objects.get(id=object_id)
        except ObjectDoesNotExist:
            return False
        return obj.consented

    def get_changeform_initial_data(self, request) -> dict:
        initial_data = super().get_changeform_initial_data(request)
        initial_data["safe_save_id"] = get_uuid()
        return initial_data
