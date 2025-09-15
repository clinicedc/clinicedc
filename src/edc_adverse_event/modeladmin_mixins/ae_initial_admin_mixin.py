from django.contrib import admin
from django.contrib.admin import display
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple

from edc_action_item.fieldsets import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_constants.constants import NOT_APPLICABLE
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_notification.utils import get_email_contacts
from edc_pdf_reports.admin import PdfButtonModelAdminMixin, print_selected_to_pdf_action

from ..forms import AeInitialForm
from ..models import AeClassification
from ..templatetags.edc_adverse_event_extras import (
    format_ae_description,
    select_description_template,
)
from .list_filters import AeAwarenessListFilter, AeClassificationListFilter
from .modeladmin_mixins import AdverseEventModelAdminMixin

fieldset_part_one = (
    "Part 1: Description",
    {
        "fields": (
            "ae_classification",
            "ae_classification_other",
            "ae_description",
            "ae_awareness_date",
            "ae_start_date",
            "ae_grade",
        )
    },
)

fieldset_part_two = (
    "Part 2: Cause and relationship to study",
    {
        "fields": (
            "ae_study_relation_possibility",
            "study_drug_relation",
            "ae_cause",
            "ae_cause_other",
        )
    },
)

fieldset_part_three = ("Part 3: Treatment", {"fields": ("ae_treatment",)})

fieldset_part_four = (
    "Part 4: SAE / SUSAR",
    {"fields": ("sae", "sae_reason", "susar", "susar_reported")},
)

default_radio_fields = {
    "ae_cause": admin.VERTICAL,
    "ae_classification": admin.VERTICAL,
    "ae_grade": admin.VERTICAL,
    "ae_study_relation_possibility": admin.VERTICAL,
    "study_drug_relation": admin.VERTICAL,
    "sae": admin.VERTICAL,
    "sae_reason": admin.VERTICAL,
    "susar": admin.VERTICAL,
    "susar_reported": admin.VERTICAL,
}


@admin.action(permissions=["view"], description="Print AE Initial Reports as PDF")
def print_to_pdf_action(modeladmin, request, queryset):
    return print_selected_to_pdf_action(modeladmin, request, queryset)


class AeInitialModelAdminMixin(
    PdfButtonModelAdminMixin,
    AdverseEventModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    ActionItemModelAdminMixin,
):
    form = AeInitialForm

    ordering = ("-ae_awareness_date",)

    actions = [print_to_pdf_action]

    email_contact = get_email_contacts("ae_reports")
    additional_instructions = format_html(  # nosec B308, B703
        "Complete the initial AE report and forward to the TMG. "
        'Email to <a href="mailto:{}">{}</a>',
        mark_safe(email_contact),  # noqa: S308
        mark_safe(email_contact),  # noqa: S308
    )

    fieldsets = (
        (None, {"fields": ("subject_identifier", "report_datetime")}),
        fieldset_part_one,
        fieldset_part_two,
        fieldset_part_three,
        fieldset_part_four,
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = default_radio_fields

    search_fields = (
        "subject_identifier",
        "action_identifier",
        "ae_description",
        "ae_classification__name",
        "ae_classification_other",
    )

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier_column",
            "dashboard",
            "pdf_button",
            "description_column",
            "documents_column",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            AeAwarenessListFilter,
            "ae_grade",
            AeClassificationListFilter,
            "sae",
            "sae_reason",
            "susar",
            "susar_reported",
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_search_fields(self, request) -> tuple[str, ...]:
        fields = super().get_search_fields(request=request)
        custom_fields = ("ae_description",)
        return custom_fields + tuple(f for f in fields if f not in custom_fields)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ae_classification":
            kwargs["queryset"] = AeClassification.objects.exclude(name=NOT_APPLICABLE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @display(description="Description", ordering="-ae_awareness_date")
    def description_column(self, obj=None):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        context = format_ae_description({}, obj, None)
        return render_to_string(select_description_template("aeinitial"), context)
