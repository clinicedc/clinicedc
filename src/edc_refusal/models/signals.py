from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from edc_screening.utils import get_subject_screening_model_cls

from ..utils import get_subject_refusal_model


@receiver(
    post_save,
    weak=False,
    dispatch_uid="subject_refusal_on_post_save",
)
def subject_refusal_on_post_save(sender, instance, raw, created, **kwargs):
    """Updates `refused` field on SubjectScreening."""
    if not raw and sender._meta.label_lower == get_subject_refusal_model():
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
    dispatch_uid="subject_refusal_on_post_delete",
)
def subject_refusal_on_post_delete(sender, instance, using, **kwargs):
    """Updates/resets `refused` field on SubjectScreening."""
    if sender._meta.label_lower == get_subject_refusal_model():
        try:
            obj = get_subject_screening_model_cls().objects.get(
                screening_identifier=instance.screening_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            obj.refused = False
            obj.save(update_fields=["refused"])
