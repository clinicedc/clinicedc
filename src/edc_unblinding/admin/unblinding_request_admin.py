from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_unblinding_admin
from ..forms import UnblindingRequestForm
from ..models import UnblindingRequest


@admin.register(UnblindingRequest, site=edc_unblinding_admin)
class UnblindingRequestAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    form = UnblindingRequestForm

    additional_instructions = (
        "Note: if the patient is deceased, complete the Death Report "
        "before completing this form. "
    )

    fieldsets = (
        (
            "Request",
            {
                "fields": (
                    "report_datetime",
                    "subject_identifier",
                    "initials",
                    "requestor",
                    "unblinding_reason",
                )
            },
        ),
        ("Approval", {"fields": ("approved", "approved_datetime")}),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    autocomplete_fields = ["requestor"]

    readonly_fields = ("approved", "approved_datetime")

    radio_fields = {"approved": admin.VERTICAL}

    list_display = (
        "subject_identifier",
        "dashboard",
        "requestor",
        "approved",
        "approved_datetime",
        "action_identifier",
        "created",
    )
