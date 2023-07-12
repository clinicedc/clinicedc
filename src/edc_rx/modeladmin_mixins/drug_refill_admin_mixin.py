from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


class DrugRefillAdminMixin:
    form = None

    inlines = []

    fieldsets_move_to_end = [crf_status_fieldset_tuple[0], audit_fieldset_tuple[0]]

    additional_instructions = format_html(
        '<span style="color:orange">Note: Medications CRF must be completed first.</span>'
    )

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Refill Information",
            {
                "fields": (
                    "rx",
                    "rx_other",
                    "rx_modified",
                    "modifications",
                    "modifications_other",
                    "modifications_reason",
                    "modifications_reason_other",
                    "rx_days",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )
    filter_horizontal = ["rx", "modifications", "modifications_reason"]

    radio_fields = {
        "crf_status": admin.VERTICAL,
        "rx_modified": admin.VERTICAL,
    }
