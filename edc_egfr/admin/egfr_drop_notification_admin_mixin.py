from typing import Dict, Optional, Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_crf.fieldset import crf_status_fieldset


class EgfrDropNotificationAdminMixin:

    radio_fields = {
        "report_status": admin.VERTICAL,
        "creatinine_units": admin.VERTICAL,
    }

    def get_fieldsets(
        self, request, obj=None
    ) -> Tuple[Tuple[Optional[str], Dict[str, Tuple[str, ...]]], ...]:
        fieldsets = [
            (None, {"fields": ("subject_visit", "report_datetime")}),
            (
                "eGFR",
                {
                    "fields": (
                        "egfr_percent_change",
                        "creatinine_date",
                        "creatinine_value",
                        "creatinine_units",
                    )
                },
            ),
            (
                "Narrative",
                {"fields": ("narrative", "report_status")},
            ),
            crf_status_fieldset,
        ]
        if getattr(self.model, "action_name", None):
            fieldsets.append(action_fieldset_tuple)
        fieldsets.append(audit_fieldset_tuple)
        return tuple(fieldsets)

    def get_search_fields(self, request) -> Tuple[str, ...]:
        fields = super().get_search_fields(request)
        custom_fields = (
            "subject_visit__subject_identifier",
            "action_identifier",
            "tracking_identifier",
        )
        return tuple(f for f in fields if f not in custom_fields) + custom_fields

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        fields = super().get_readonly_fields(request, obj)
        return (
            "creatinine_date",
            "creatinine_value",
            "creatinine_units",
            "egfr_percent_change",
        ) + fields

    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        return ("report_status", "creatinine_date") + list_filter

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "report_status",
            "report_datetime",
            "egfr_percent_change",
            "creatinine_date",
            "creatinine_value",
        )
        return tuple(f for f in list_display if f not in custom_fields) + custom_fields
