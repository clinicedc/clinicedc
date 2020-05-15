from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, INCOMPLETE
from edc_crf.models import CrfStatus


def update_crf_status_for_instance(instance, crf_status):
    """Only works for CRFs, e.g. have subject_visit."""
    if hasattr(instance, "subject_visit"):
        opts = dict(
            subject_identifier=instance.subject_visit.subject_identifier,
            visit_schedule_name=instance.subject_visit.visit_schedule_name,
            schedule_name=instance.subject_visit.schedule_name,
            visit_code=instance.subject_visit.visit_code,
            visit_code_sequence=instance.subject_visit.visit_code_sequence,
            label_lower=instance._meta.label_lower,
            user_created=instance.user_created,
            user_modified=instance.user_modified,
        )

        if crf_status == COMPLETE:
            CrfStatus.objects.filter(**opts).delete()
        elif crf_status == INCOMPLETE:
            try:
                CrfStatus.objects.get(**opts)
            except ObjectDoesNotExist:
                CrfStatus.objects.create(**opts)


@receiver(
    post_save, weak=False, dispatch_uid="update_crf_status_post_save",
)
def update_crf_status_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw and not kwargs.get("update_fields"):
        if ".historical" not in instance._meta.label_lower:
            try:
                crf_status = instance.crf_status
            except AttributeError as e:
                if "crf_status" not in str(e):
                    raise AttributeError(str(e))
            else:
                update_crf_status_for_instance(instance, crf_status)
