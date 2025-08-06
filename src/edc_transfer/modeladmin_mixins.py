from typing import Tuple

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple


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

    filter_horizontal = ("transfer_reason",)

    radio_fields = {
        "initiated_by": admin.VERTICAL,
        "may_return": admin.VERTICAL,
        "may_contact": admin.VERTICAL,
    }

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "transfer_date",
            "initiated_by",
            "may_return",
            "may_contact",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    #
    def get_list_filter(self, request) -> Tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            "transfer_date",
            "initiated_by",
            "may_return",
            "may_contact",
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        custom_fields = ("subject_identifier",)
        return tuple(set(custom_fields + search_fields))
