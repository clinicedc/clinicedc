from django.apps import apps as django_apps
from edc_constants.constants import NEW
from edc_metadata import REQUIRED

from ..constants import COMPLETE_APPT, IN_PROGRESS_APPT, INCOMPLETE_APPT, NEW_APPT


def appointment_mark_as_done(modeladmin, request, queryset):
    """Update appointment to DONE.

    If a record exists in CrfStatus, set to INCOMPLETE.
    """
    crfstatus_model_cls = django_apps.get_model("edc_crf.crfstatus")
    crfmetadata_model_cls = django_apps.get_model("edc_metadata.crfmetadata")

    for obj in queryset.filter(
        appt_status__in=[COMPLETE_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT]
    ):
        if crfstatus_model_cls.objects.filter(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule_name,
            schedule_name=obj.schedule_name,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
        ).exists():
            obj.appt_status = INCOMPLETE_APPT
            obj.save(update_fields=["appt_status"])
        else:
            if crfmetadata_model_cls.objects.filter(
                subject_identifier=obj.subject_identifier,
                visit_schedule_name=obj.visit_schedule_name,
                schedule_name=obj.schedule_name,
                visit_code=obj.visit_code,
                visit_code_sequence=obj.visit_code_sequence,
                entry_status=REQUIRED,
            ).exists():
                obj.appt_status = INCOMPLETE_APPT
            else:
                obj.appt_status = COMPLETE_APPT
            obj.save(update_fields=["appt_status"])


# noinspection PyTypeHints
appointment_mark_as_done.short_description = "Mark as DONE (if allowed)"  # type: ignore


def appointment_mark_as_new(modeladmin, request, queryset):
    """Update appointment to NEW."""
    crfmetadata_model_cls = django_apps.get_model("edc_metadata.crfmetadata")
    for obj in queryset.filter(appt_status__in=[NEW, COMPLETE_APPT]):
        if not crfmetadata_model_cls.objects.filter(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule_name,
            schedule_name=obj.schedule_name,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
        ).exists():
            obj.appt_status = NEW_APPT
            obj.save(update_fields=["appt_status"])


# noinspection PyTypeHints
appointment_mark_as_new.short_description = "Mark as NEW (if allowed)"  # type: ignore
