from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_unblinding_admin
from ..forms import UnblindingReviewForm
from ..models import UnblindingReview


@admin.register(UnblindingReview, site=edc_unblinding_admin)
class UnblindingReviewAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    form = UnblindingReviewForm

    fieldsets = (
        ("Request", {"fields": ("subject_identifier", "report_datetime", "reviewer")}),
        ("Approval", {"fields": ("approved", "comment")}),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    autocomplete_fields = ["reviewer"]

    list_display = (
        "subject_identifier",
        "dashboard",
        "report_datetime",
        "reviewer",
        "approved",
        "action_identifier",
        "created",
    )

    radio_fields = {"approved": admin.VERTICAL}
