from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fields, action_fieldset_tuple

from .forms import LtfuForm


class LtfuModelAdminMixin:

    form = LtfuForm

    fieldsets = (
        (None, {"fields": ("subject_identifier", "report_datetime")}),
        (
            "Loss to followup",
            {
                "fields": (
                    "last_seen_datetime",
                    "number_consecutive_missed_visits",
                    "last_missed_visit_datetime",
                    "home_visited",
                    "home_visit_detail",
                    "ltfu_category",
                    "ltfu_category_other",
                    "ltfu_date",
                    "comment",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "dashboard",
        "ltfu_date",
        "number_consecutive_missed_visits",
        "home_visited",
    )

    list_filter = (
        "ltfu_date",
        "last_seen_datetime",
        "last_missed_visit_datetime",
        "number_consecutive_missed_visits",
    )

    radio_fields = {
        "home_visited": admin.VERTICAL,
        "ltfu_category": admin.VERTICAL,
    }

    search_fields = ("subject_identifier", "action_identifier", "tracking_identifier")

    def get_readonly_fields(self, request, obj=None) -> tuple:
        fields = super().get_readonly_fields(request, obj)
        return action_fields + fields
