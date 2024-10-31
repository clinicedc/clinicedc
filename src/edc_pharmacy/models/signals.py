from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, PARTIAL

from ..dispense import Dispensing
from ..model_mixins import StudyMedicationCrfModelMixin
from ..utils import update_previous_refill_end_datetime
from .dispensing_history import DispensingHistory
from .stock import OrderItem, ReceiveItem, Stock


@receiver(post_save, sender=OrderItem, dispatch_uid="update_stock_on_post_save")
def update_order_item_on_post_save(sender, instance, raw, created, **kwargs):
    """Update qty counters on Order model each time OrderItem is
    saved.
    """
    if not raw:
        order_items = OrderItem.objects.filter(order=instance.order)
        instance.order.unit_qty = order_items.aggregate(unit_qty=Sum("unit_qty"))["unit_qty"]
        instance.order.container_qty = order_items.aggregate(
            container_qty=Sum("container_qty")
        )["container_qty"]
        instance.order.save()


@receiver(post_save, sender=ReceiveItem, dispatch_uid="update_stock_on_post_save")
def update_order_item_qty_received_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
):
    """Update received counters on OrderItem, Order models and add to
    Stock each time ReceiveItem is saved.
    """
    if not raw and update_fields != ["added_to_stock"]:
        instance.order_item.container_qty_received = instance.container_qty
        if instance.order_item.container_qty_received == instance.order_item.container_qty:
            instance.order_item.status = COMPLETE
        elif instance.order_item.container_qty > instance.order_item.container_qty_received:
            instance.order_item.status = PARTIAL
        instance.order_item.save()

        order = instance.receive.order
        container_qty_received = OrderItem.objects.filter(order=order).aggregate(
            container_qty_received=Sum("container_qty_received")
        )["container_qty_received"]
        if order.container_qty == container_qty_received:
            order.status = COMPLETE
            order.save()

        # add to stock
        Stock.objects.create(
            receive_item=instance,
            unit_qty_in=instance.unit_qty,
            container_qty_in=instance.container_qty,
            container=instance.container,
            location=instance.receive.location,
        )
        instance.added_to_stock = True
        instance.save_base(update_fields=["added_to_stock"])


# @receiver(post_save, sender=Receive, dispatch_uid="update_stock_on_post_save")
# def update_stock_on_post_save(sender, instance, raw, created, **kwargs):
#     if not raw:
#         for identifier in instance.stock_identifiers_as_list():
#             try:
#                 obj = Stock.objects.get(stock_identifier=identifier)
#             except ObjectDoesNotExist:
#                 obj = Stock(
#                     stock_identifier=identifier,
#                     receiving=instance,
#                     product=instance.product,
#                     warehouse=instance.warehouse,
#                 )
#                 obj.save()
#             else:
#                 obj.receiving = instance
#                 obj.product = instance.product
#                 obj.warehouse = instance.warehouse
#                 obj.save()


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


@receiver(
    post_save,
    dispatch_uid="update_refill_end_datetime",
)
def update_previous_refill_end_datetime_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
):
    if not raw and not update_fields:
        if isinstance(instance, (StudyMedicationCrfModelMixin,)):
            update_previous_refill_end_datetime(instance)
