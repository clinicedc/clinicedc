from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_pharmacy.dispensing import Dispensing

from .dispensing_history import DispensingHistory


@receiver(
    post_save, sender=DispensingHistory, dispatch_uid="dispensing_history_on_post_save"
)
def dispensing_history_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        dispensing = Dispensing(
            rx_refill=instance.rx_refill, dispensed=instance.dispensed
        )
        instance.rx_refill.remaining = dispensing.remaining
        instance.rx_refill.save(update_fields=["remaining"])


@receiver(
    post_delete,
    sender=DispensingHistory,
    dispatch_uid="dispensing_history_on_post_delete",
)
def dispensing_history_on_post_delete(sender, instance, using=None, **kwargs):
    dispensing = Dispensing(rx_refill=instance.rx_refill, dispensed=instance.dispensed)
    instance.rx_refill.remaining = dispensing.remaining
    instance.rx_refill.save(update_fields=["remaining"])
