from django.db.models.signals import post_save
from django.dispatch import receiver

from .update_crf_status_for_instance import update_crf_status_for_instance


@receiver(
    post_save,
    weak=False,
    dispatch_uid="update_crf_status_post_save",
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
