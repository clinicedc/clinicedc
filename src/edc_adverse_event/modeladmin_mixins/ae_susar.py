from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from .modeladmin_mixins import NonAeInitialModelAdminMixin


# @admin.register(AeSusar, site=ambition_ae_admin)
class AeSusarModelAdminMixin(
    ModelAdminSubjectDashboardMixin, NonAeInitialModelAdminMixin
):

    form = None  # AeSusarForm

    list_display = [
        "subject_identifier",
        "dashboard",
        "status",
        "ae_initial",
        "report_datetime",
        "submitted_datetime",
    ]

    list_filter = ("report_datetime", "submitted_datetime")

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
        "ae_initial__tracking_identifier",
        "tracking_identifier",
    ]

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

    def status(self, obj=None):
        return obj.report_status.title()
