from django.contrib import admin
from django.template.loader import render_to_string
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ModelAdminActionItemMixin
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..forms import AeSusarForm
from ..templatetags.edc_adverse_event_extras import (
    format_ae_susar_description,
    select_description_template,
)
from .modeladmin_mixins import AdverseEventModelAdminMixin, NonAeInitialModelAdminMixin


class AeSusarModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    AdverseEventModelAdminMixin,
    ModelAdminActionItemMixin,
):

    form = AeSusarForm

    list_display = [
        "subject_identifier",
        "dashboard",
        "description",
        "initial_ae",
        "user",
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

    def description(self, obj):
        """Returns a formatted comprehensive description."""
        context = format_ae_susar_description({}, obj, 50)
        return render_to_string(select_description_template("aesusar"), context)
