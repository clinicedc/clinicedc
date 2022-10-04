from django.contrib import admin
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple

missed_medications_fieldset_tuple = (
    "Missed Medications",
    {
        "description": format_html(
            "<H5><B><font color='orange'>Interviewer to read</font></B></H5>"
            "<p>People may miss taking their "
            "medicines for various reasons. What was the reason you "
            "missed taking your pills the last time?</p>"
        ),
        "fields": (
            "last_missed_pill",
            "missed_pill_reason",
            "other_missed_pill_reason",
        ),
    },
)

pill_count_fieldset_tuple = (
    "Pill Count",
    {
        "fields": ("pill_count_performed", "pill_count", "pill_count_not_performed_reason"),
    },
)


def get_visual_score_fieldset_tuple(description=None):
    description = (
        description
        or """
    <H5><B><font color="orange">Interviewer to read</font></B></H5>
    <p>Drag the slider on the line below at
    the point showing your best guess about how much study medication
    you have taken in the last 14 days or in the last 28 days as
    appropriate:<BR><BR>
    <B>0%</B> means you have taken no study pills<BR>
    <B>50%</B> means you have taken half of your study pills<BR>
    <B>100%</B> means you have taken all your study pills<BR>
    </p>
    """
    )

    return (
        "Visual Score",
        {
            "description": format_html(description or ""),
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
        pill_count_fieldset_tuple,
        missed_medications_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {"last_missed_pill": admin.VERTICAL}

    filter_horizontal = ("missed_pill_reason",)
