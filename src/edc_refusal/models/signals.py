from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_screening.utils import get_subject_screening_model_cls

from ..utils import get_subject_refusal_model_cls


@receiver(
    post_save,
    weak=False,
    sender=get_subject_refusal_model_cls(),
    dispatch_uid="subject_refusal_on_post_save",
)
def subject_refusal_on_post_save(sender, instance, raw, created, **kwargs):
    """Updates `refused` field on SubjectScreening"""
    if not raw:
        try:
            obj = get_subject_screening_model_cls().objects.get(
                screening_identifier=instance.screening_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            obj.refused = True
            obj.save(update_fields=["refused"])


@receiver(
    post_delete,
    weak=False,
    sender=get_subject_refusal_model_cls(),
    dispatch_uid="subject_refusal_on_post_delete",
)
def subject_refusal_on_post_delete(sender, instance, using, **kwargs):
    """Updates/Resets subject screening."""
    try:
        obj = get_subject_screening_model_cls().objects.get(
            screening_identifier=instance.screening_identifier
        )
    except ObjectDoesNotExist:
        pass
    else:
        obj.refused = False
        obj.save(update_fields=["refused"])
