from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_action_item import (
    ActionItemModelAdminMixin,
    action_fields,
    action_fieldset_tuple,
)
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin


class HospitalizationModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    ActionItemModelAdminMixin,
):
    form = None

    fieldsets = (
        (None, {"fields": ("subject_identifier", "report_datetime")}),
        (
            "Hospital admission",
            {
                "fields": (
                    "have_details",
                    "admitted_date",
                    "admitted_date_estimated",
                )
            },
        ),
        (
            "Hospital discharge",
            {
                "fields": (
                    "discharged",
                    "discharged_date",
                    "discharged_date_estimated",
                )
            },
        ),
        ("Narrative", {"fields": ("narrative",)}),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = ("subject_identifier", "action_identifier")

    radio_fields = {
        "admitted_date_estimated": admin.VERTICAL,
        "discharged": admin.VERTICAL,
        "discharged_date_estimated": admin.VERTICAL,
        "have_details": admin.VERTICAL,
    }

    search_fields = ("subject_identifier", "action_identifier")

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        action_flds = tuple(fld for fld in action_fields if fld != "action_identifier")
        return tuple(set(action_flds + readonly_fields))
