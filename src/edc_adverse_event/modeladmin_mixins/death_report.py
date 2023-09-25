from __future__ import annotations

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin


class DeathReportModelAdminMixin(ModelAdminSubjectDashboardMixin, ActionItemModelAdminMixin):
    form = None

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "death_datetime",
                    "study_day",
                    "death_as_inpatient",
                )
            },
        ),
        (
            "Opinion of Local Study Doctor",
            {"fields": ("cause_of_death", "cause_of_death_other", "narrative")},
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "death_as_inpatient": admin.VERTICAL,
        "cause_of_death": admin.VERTICAL,
    }

    def get_search_fields(self, request) -> tuple[str]:
        search_fields = super().get_search_fields(request)
        custom_fields = ("subject_identifier", "action_identifier")
        return tuple(set(search_fields + custom_fields))

    def get_list_display(self, request) -> tuple[str]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "report_datetime",
            "cause_of_death",
            "death_datetime",
            "action_item",
            "parent_action_item",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> tuple[str]:
        list_filter = super().get_list_filter(request)
        custom_fields = ("report_datetime", "death_datetime", "cause_of_death")
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)
