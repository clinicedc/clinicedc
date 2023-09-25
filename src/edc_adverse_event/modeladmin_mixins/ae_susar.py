from __future__ import annotations

from django.contrib import admin
from django.template.loader import render_to_string
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..forms import AeSusarForm
from ..templatetags.edc_adverse_event_extras import (
    format_ae_susar_description,
    select_description_template,
)
from .modeladmin_mixins import AdverseEventModelAdminMixin, NonAeInitialModelAdminMixin


class AeSusarModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    AdverseEventModelAdminMixin,
    ActionItemModelAdminMixin,
):
    form = AeSusarForm

    search_fields = (
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "submitted_datetime",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {"report_status": admin.VERTICAL}

    def get_list_display(self, request) -> tuple[str]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "description",
            "initial_ae",
            "user",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> tuple[str]:
        list_filter = super().get_list_filter(request)
        custom_fields = ("report_datetime", "submitted_datetime")
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    @staticmethod
    def description(obj=None) -> str:
        """Returns a formatted comprehensive description."""
        context = format_ae_susar_description({}, obj, 50)
        return render_to_string(select_description_template("aesusar"), context)
