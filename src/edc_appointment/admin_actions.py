from edc_appointment.constants import COMPLETE_APPT, INCOMPLETE_APPT
from edc_crf.models import CrfStatus


def appointment_mark_as_done(modeladmin, request, queryset):
    """Update appointment to DONE.

    If a record exists in CrfStatus, set to INCOMPLETE.
    """
    for obj in queryset:
        if CrfStatus.objects.filter(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule_name,
            schedule_name=obj.schedule_name,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
        ).exists():
            obj.appt_status = INCOMPLETE_APPT
        else:
            obj.appt_status = COMPLETE_APPT
        obj.save()


appointment_mark_as_done.short_description = "Mark as done (if done)"
