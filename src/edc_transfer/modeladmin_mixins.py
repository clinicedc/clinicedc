from copy import copy
from typing import Tuple

from django.contrib import admin
from edc_action_item import action_fields, action_fieldset_tuple
from edc_model_admin import audit_fieldset_tuple


class SubjectTransferModelAdminMixin:

    form = None

    fieldsets = (
        (None, {"fields": ("subject_identifier", "report_datetime")}),
        (
            "Transfer Details",
            {
                "fields": (
                    "transfer_date",
                    "initiated_by",
                    "initiated_by_other",
                    "transfer_reason",
                    "transfer_reason_other",
                    "may_return",
                    "may_contact",
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
        "transfer_date",
        "initiated_by",
        "may_return",
        "may_contact",
    )

    list_filter = (
        "transfer_date",
        "initiated_by",
        "may_return",
        "may_contact",
    )

    filter_horizontal = ("transfer_reason",)

    radio_fields = {
        "initiated_by": admin.VERTICAL,
        "may_return": admin.VERTICAL,
        "may_contact": admin.VERTICAL,
    }

    search_fields = ("subject_identifier", "action_identifier", "tracking_identifier")

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj)
        return tuple(set(action_fields + readonly_fields))
