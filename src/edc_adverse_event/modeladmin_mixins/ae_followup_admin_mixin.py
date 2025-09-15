from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import display
from django.template.loader import render_to_string
from django_audit_fields.admin import audit_fieldset_tuple

from edc_action_item.fieldsets import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..forms import AeFollowupForm
from ..templatetags.edc_adverse_event_extras import (
    format_ae_followup_description,
    select_description_template,
)
from .modeladmin_mixins import AdverseEventModelAdminMixin, NonAeInitialModelAdminMixin


class AeFollowupModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    AdverseEventModelAdminMixin,
    ActionItemModelAdminMixin,
):
    form = AeFollowupForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "outcome_date",
                    "outcome",
                    "ae_grade",
                    "relevant_history",
                    "followup",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {  # noqa: RUF012
        "outcome": admin.VERTICAL,
        "followup": admin.VERTICAL,
        "ae_grade": admin.VERTICAL,
    }

    def get_search_fields(self, request) -> tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        return tuple(
            {
                *search_fields,
                "action_identifier",
                "ae_initial__subject_identifier",
                "ae_initial__action_identifier",
            }
        )

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier_column",
            "dashboard",
            "description_column",
            "documents_column",
        )
        return tuple({*list_display, *custom_fields})

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            "ae_grade",
            "followup",
            "outcome_date",
            "outcome",
            "report_datetime",
        )
        return tuple({*list_filter, *custom_fields})

    @display(description="Description", ordering="-report_datetime")
    def description_column(self, obj):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        context = format_ae_followup_description({}, obj, None)
        return render_to_string(select_description_template("aefollowup"), context)
