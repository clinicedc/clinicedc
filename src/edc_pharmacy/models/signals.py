from uuid import uuid4

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ..dispense import Dispensing
from ..refill import create_refills_from_crf
from .dispensing_history import DispensingHistory
from .stock_create_labels import Labels, StockCreateLabels


@receiver(post_save, sender=DispensingHistory, dispatch_uid="dispensing_history_on_post_save")
def dispensing_history_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        dispensing = Dispensing(rx_refill=instance.rx_refill, dispensed=instance.dispensed)
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


@receiver(
    post_save,
    dispatch_uid="create_refills_on_post_save",
)
def create_refills_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    if not raw and not update_fields:
        try:
            instance.creates_refills_from_crf
        except AttributeError:
            pass
        else:
            if instance.creates_refills_from_crf:
                create_refills_from_crf(instance)


@receiver(
    post_save,
    sender=StockCreateLabels,
    dispatch_uid="create_stock_labels_on_post_save",
)
def create_stock_labels_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        qty_already_created = Labels.objects.filter(stock_create_labels=instance).count()
        for i in range(0, instance.qty - qty_already_created):
            Labels.objects.create(stock_create_labels=instance, stock_identifier=uuid4().hex)
