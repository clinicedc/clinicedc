from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from edc_appointment.constants import ONTIME_APPT
from edc_constants.constants import NOT_APPLICABLE, PATIENT
from edc_metadata import REQUIRED
from edc_metadata.metadata import CrfMetadataGetter
from edc_pharmacy.constants import IN_PROGRESS_APPT

from ..constants import SCHEDULED
from ..model_mixins import SubjectVisitMissedModelMixin


@receiver(post_save, weak=False, dispatch_uid="visit_tracking_check_in_progress_on_post_save")
def visit_tracking_check_in_progress_on_post_save(
    sender, instance, raw, created, using, update_fields, **kwargs
):
    """Calls method on the visit tracking instance"""
    if not raw and not update_fields:
        try:
            instance.appointment  # noqa: B018
        except AttributeError:
            pass
        else:
            try:
                instance.update_appointment_status()
            except AttributeError as e:
                if "update_appointment_status" not in str(e):
                    raise


@receiver(post_delete, weak=False, dispatch_uid="subject_visit_missed_on_post_delete")
def subject_visit_missed_on_post_delete(sender, instance, using, **kwargs) -> None:
    if isinstance(instance, (SubjectVisitMissedModelMixin,)):
        appointment = instance.related_visit.appointment
        # need to remove references and missed visit metadata manually
        getter = CrfMetadataGetter(appointment)
        getter.metadata_objects.filter(model=instance._meta.label_lower).update(
            entry_status=REQUIRED
        )
        # update appointment
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.appt_timing = ONTIME_APPT
        appointment.modified = instance.modified
        appointment.user_modified = instance.user_modified
        appointment.save_base(
            update_fields=["appt_status", "appt_timing", "modified", "user_modified"]
        )
        if appointment.visit_code_sequence == 0:
            # update related visit. Visit code sequence should always be 0
            instance.related_visit.reason = SCHEDULED
            instance.related_visit.reason_unscheduled = NOT_APPLICABLE
            instance.related_visit.info_source = PATIENT
            instance.related_visit.info_source_other = ""
            instance.related_visit.comment = ""
            instance.related_visit.modified = instance.modified
            instance.related_visit.user_modified = instance.user_modified
            instance.related_visit.save_base(
                update_fields=[
                    "reason",
                    "reason_unscheduled",
                    "info_source",
                    "modified",
                    "user_modified",
                ]
            )
