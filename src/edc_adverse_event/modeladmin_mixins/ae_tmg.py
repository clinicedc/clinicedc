from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ModelAdminActionItemMixin
from edc_constants.constants import OTHER
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_utils import convert_php_dateformat

from ..forms import AeTmgForm
from ..get_ae_model import get_ae_model
from .modeladmin_mixins import NonAeInitialModelAdminMixin


class AeTmgModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    ModelAdminActionItemMixin,
):

    form = AeTmgForm

    additional_instructions = "For completion by TMG Investigators Only"

    list_display = [
        "subject_identifier",
        "dashboard",
        "status",
        "ae_initial",
        "report_datetime",
        "officials_notified",
        "report_closed_datetime",
    ]

    list_filter = ("report_datetime", "report_status")

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
        "ae_initial__tracking_identifier",
        "tracking_identifier",
    ]

    fieldsets = (
        (None, {"fields": ("subject_identifier", "ae_initial", "report_datetime")}),
        (
            "Original Report",
            {
                "fields": (
                    "ae_description",
                    "ae_classification",
                    "ae_classification_other",
                )
            },
        ),
        (
            "Investigator's section",
            {
                "fields": (
                    "ae_received_datetime",
                    "clinical_review_datetime",
                    "investigator_comments",
                    "original_report_agreed",
                    "narrative",
                    "officials_notified",
                    "report_status",
                    "report_closed_datetime",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "report_status": admin.VERTICAL,
        "original_report_agreed": admin.VERTICAL,
    }

    def status(self, obj=None):
        return obj.report_status.title()

    def get_queryset(self, request):
        """Returns for the current user if has `view_aetmg` permissions."""
        # TODO: this used to look at group membership?
        if request.user.has_perm(f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aetmg"):
            return super().get_queryset(request).all()
        return super().get_queryset(request)

    def get_changeform_initial_data(self, request):
        """Updates initial data with the description of the
        original AE.
        """
        initial = super().get_changeform_initial_data(request)
        AeInitial = get_ae_model("aeinitial")
        try:
            ae_initial = AeInitial.objects.get(pk=request.GET.get("ae_initial"))
        except ObjectDoesNotExist:
            pass
        else:
            try:
                ae_classification = ae_initial.ae_classification.name
            except AttributeError:
                ae_classification = None
            else:
                if ae_initial.ae_classification.name == OTHER:
                    other = ae_initial.ae_classification_other.rstrip()
                    ae_classification = f"{ae_classification}: {other}"
                report_datetime = ae_initial.report_datetime.strftime(
                    convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
                )
            initial.update(
                ae_classification=ae_classification,
                ae_description=(f"{ae_initial.ae_description} (reported: {report_datetime})"),
            )
        return initial
