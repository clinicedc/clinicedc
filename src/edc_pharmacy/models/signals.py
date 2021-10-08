from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .dispensing_history import DispensingHistory


@receiver(
    post_save, sender=DispensingHistory, dispatch_uid="dispensing_history_on_post_save"
)
def dispensing_history_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        instance.prescription_item.save()


@receiver(
    post_delete,
    sender=DispensingHistory,
    dispatch_uid="dispensing_history_on_post_delete",
)
def dispensing_history_on_post_save(sender, instance, using=None, **kwargs):
    instance.prescription_item.save()
