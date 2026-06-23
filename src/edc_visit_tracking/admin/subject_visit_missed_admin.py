from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from edc_form_label.form_label_modeladmin_mixin import FormLabelModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_visit_tracking_admin
from ..forms import SubjectVisitMissedForm
from ..modeladmin_mixins import CrfModelAdminMixin
from ..models import SubjectVisitMissed


@admin.register(SubjectVisitMissed, site=edc_visit_tracking_admin)
class SubjectVisitMissedAdmin(
    CrfModelAdminMixin, FormLabelModelAdminMixin, SimpleHistoryAdmin
):
    form = SubjectVisitMissedForm

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Contact History",
            {
                "fields": (
                    "survival_status",
                    "contact_attempted",
                    "contact_made",
                    "contact_attempts_count",
                    "contact_attempts_explained",
                    "contact_last_date",
                    "missed_reasons",
                    "missed_reasons_other",
                    "comment",
                ),
            },
        ),
        audit_fieldset_tuple,
    )

    filter_horizontal = ("missed_reasons",)

    radio_fields = {  # noqa: RUF012
        "survival_status": admin.VERTICAL,
        "contact_attempted": admin.VERTICAL,
        "contact_made": admin.VERTICAL,
    }
