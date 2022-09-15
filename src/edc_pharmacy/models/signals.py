from uuid import uuid4

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ..dispense import Dispensing
from .dispensing_history import DispensingHistory

# from .order import Order
# from .rx_refill import RxRefill
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
    dispatch_uid="create_or_update_refills_on_post_save",
)
def create_or_update_refills_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
):
    if not raw:
        try:
            instance.related_visit_model_attr()  # see edc-visit-tracking
        except AttributeError:
            pass
        else:
            try:
                instance.creates_refills_from_crf()
            except AttributeError as e:
                if "creates_refills_from_crf" not in str(e):
                    raise
                pass


# @receiver(
#     post_save,
#     sender=RxRefill,
#     dispatch_uid="create_or_update_refills_on_post_save",
# )
# def get_or_create_subject_orders_on_refill(
#     sender, instance, raw, created, update_fields, **kwargs
# ):
#     """Confirm or create an order for the items requested thru the refill"""
#     if not raw:
#         pass
#         instance.total
#         Order.objects.filter(product=product)
#         # check orders
#         # is the product requested on order
#         # is the product requested on order and delivered to
#         # check patient_stock


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
