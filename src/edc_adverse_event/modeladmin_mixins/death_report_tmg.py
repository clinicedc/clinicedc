from __future__ import annotations

from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_constants.constants import OTHER
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..utils import get_ae_model


class DeathReportTmgModelAdminMixin(
    ModelAdminSubjectDashboardMixin, ActionItemModelAdminMixin
):
    fieldsets = (
        (None, {"fields": ("subject_identifier", "death_report", "report_datetime")}),
        (
            "Opinion of TMG",
            {
                "fields": (
                    "cause_of_death",
                    "cause_of_death_other",
                    "cause_of_death_agreed",
                    "narrative",
                    "report_status",
                    "report_closed_datetime",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "cause_of_death": admin.VERTICAL,
        "cause_of_death_agreed": admin.VERTICAL,
        "report_status": admin.VERTICAL,
    }

    search_fields = (
        "subject_identifier",
        "action_identifier",
        "death_report__action_identifier",
    )

    def get_list_display(self, request) -> tuple[str]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "dashboard",
            "report_datetime",
            "cause",
            "agreed",
            "status",
            "report_closed_datetime",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> tuple[str]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
            "report_datetime",
            "report_status",
            "cause_of_death_agreed",
            "cause_of_death",
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def get_readonly_fields(self, request, obj=None) -> tuple[str]:
        fields = super().get_readonly_fields(request, obj)
        if obj:
            fields = fields + ("death_report",)
        return fields

    @staticmethod
    def status(obj=None):
        return obj.report_status.title()

    def cause(self, obj=None):
        if obj.cause_of_death.name == OTHER:
            return f"Other: {obj.cause_of_death_other}"
        return obj.cause_of_death

    cause.short_description = "Cause (TMG Opinion)"

    @staticmethod
    def agreed(obj=None):
        return obj.cause_of_death_agreed

    @property
    def death_report_model_cls(self):
        return get_ae_model("deathreport")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "death_report":
            if request.GET.get("death_report"):
                kwargs["queryset"] = self.death_report_model_cls.objects.filter(
                    id__exact=request.GET.get("death_report", 0)
                )
            else:
                kwargs["queryset"] = self.death_report_model_cls.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
