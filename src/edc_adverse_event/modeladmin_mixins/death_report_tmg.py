from copy import copy

from django.contrib import admin
from edc_action_item import action_fields, action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ModelAdminActionItemMixin
from edc_constants.constants import OTHER
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..get_ae_model import get_ae_model


class DeathReportTmgModelAdminMixin(
    ModelAdminSubjectDashboardMixin, ModelAdminActionItemMixin
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

    list_display = [
        "subject_identifier",
        "dashboard",
        "report_datetime",
        "cause",
        "agreed",
        "status",
        "report_closed_datetime",
    ]

    list_filter = (
        "report_datetime",
        "report_status",
        "cause_of_death_agreed",
        "cause_of_death",
    )

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "tracking_identifier",
        "death_report__action_identifier",
        "death_report__tracking_identifier",
    ]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        action_flds = copy(list(action_fields))
        action_flds.remove("action_identifier")
        fields = list(action_flds) + list(fields)
        if obj:
            fields = fields + ["death_report"]
        return fields

    def status(self, obj=None):
        return obj.report_status.title()

    def cause(self, obj):
        if obj.cause_of_death.name == OTHER:
            return f"Other: {obj.cause_of_death_other}"
        return obj.cause_of_death

    cause.short_description = "Cause (TMG Opinion)"

    def agreed(self, obj):
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
