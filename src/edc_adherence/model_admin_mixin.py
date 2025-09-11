from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_audit_fields.admin import audit_fieldset_tuple


def get_missed_medications_fieldset_tuple():
    description = render_to_string("edc_adherence/missed_medication_fieldset_description.html")
    return (
        _("Missed Medications"),
        {
            "description": format_html("{}", description),
            "fields": (
                "last_missed_pill",
                "missed_pill_reason",
                "other_missed_pill_reason",
            ),
        },
    )


def get_pill_count_fieldset_tuple():
    return (
        _("Pill Count"),
        {
            "fields": (
                "pill_count_performed",
                "pill_count",
                "pill_count_not_performed_reason",
            ),
        },
    )


def get_visual_score_fieldset_tuple(
    description: str | None = None, section_title: str | None = None
):
    section_title = section_title or _("Visual Score")
    description = description or render_to_string(
        "edc_adherence/visual_score_fieldset_description.html"
    )
    return (
        section_title,
        {
            "description": format_html("{}", description),
            "fields": ("visual_score_slider", "visual_score_confirmed"),
        },
    )


class MedicationAdherenceAdminMixin:
    """Declare your admin class using this mixin.

    For example:

        @admin.register(MedicationAdherence, site=my_subject_admin)
        class MedicationAdherenceAdmin(MedicationAdherenceAdminMixin, CrfModelAdmin):

            form = MedicationAdherenceForm

    """

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        get_visual_score_fieldset_tuple(),
        get_pill_count_fieldset_tuple(),
        get_missed_medications_fieldset_tuple(),
        audit_fieldset_tuple,
    )

    radio_fields = {
        "pill_count_performed": admin.VERTICAL,
        "last_missed_pill": admin.VERTICAL,
    }

    filter_horizontal = ("missed_pill_reason",)
