from uuid import uuid4

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_pharmacy.models import MedicationStockCreateLabels
from edc_pharmacy.models.medication_stock_create_labels import Labels

from ..dispensing import Dispensing
from ..refill import create_next_refill, create_refill
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


@receiver(
    post_save,
    dispatch_uid="create_refills_on_post_save",
)
def create_refills_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        try:
            instance.creates_refills_from_crf
        except AttributeError:
            pass
        else:
            if instance.creates_refills_from_crf:
                create_refill(instance)
                create_next_refill(instance)


@receiver(
    post_save,
    sender=MedicationStockCreateLabels,
    dispatch_uid="create_medication_stock_labels_on_post_save",
)
def create_medication_stock_labels_on_post_save(
    sender, instance, raw, created, **kwargs
):
    if not raw:
        qty_already_created = Labels.objects.filter(
            medication_stock_create_labels=instance
        ).count()
        for i in range(0, instance.qty - qty_already_created):
            Labels.objects.create(
                medication_stock_create_labels=instance, stock_identifier=uuid4().hex
            )
