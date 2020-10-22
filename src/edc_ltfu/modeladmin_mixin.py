from copy import copy
from django.contrib import admin
from edc_action_item import action_fieldset_tuple, action_fields
from edc_model_admin import audit_fieldset_tuple


class LossToFollowupModelAdminMixin:

    form = None

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
                    "loss_category",
                    "loss_category_other",
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
        "loss_category": admin.VERTICAL,
    }

    search_fields = ("subject_identifier", "action_identifier", "tracking_identifier")

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        action_flds = copy(list(action_fields))
        fields = list(action_flds) + list(fields)
        return fields
