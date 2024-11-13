from decimal import Decimal

from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, PARTIAL

from ..dispense import Dispensing
from ..exceptions import InsufficientStockError
from ..model_mixins import StudyMedicationCrfModelMixin
from ..utils import process_repack_request, update_previous_refill_end_datetime
from .dispensing_history import DispensingHistory
from .stock import (
    OrderItem,
    Receive,
    ReceiveItem,
    RepackRequest,
    Stock,
    StockRequestItem,
)


@receiver(post_save, sender=Stock, dispatch_uid="update_stock_on_post_save")
def stock_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update unit qty"""
    if not raw and not update_fields:
        instance.unit_qty_in = Decimal(instance.qty_in) * instance.container.qty
        if instance.from_stock:
            instance.from_stock.unit_qty_out += instance.unit_qty_in
            if instance.from_stock.unit_qty_out > instance.from_stock.unit_qty_in:
                raise InsufficientStockError("Unit QTY OUT cannot exceed Unit QTY IN.")
            instance.from_stock.save(update_fields=["unit_qty_out"])
        instance.unit_qty_out = Decimal(instance.qty_out) * instance.container.qty
        if instance.unit_qty_out > instance.unit_qty_in:
            raise InsufficientStockError("Unit QTY OUT cannot exceed Unit QTY IN.")
        instance.save(update_fields=["unit_qty_in", "unit_qty_out", "product", "description"])


@receiver(post_save, sender=OrderItem, dispatch_uid="update_order_item_on_post_save")
def order_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update item_count on Order model each time OrderItem is
    saved.
    """
    pass
    # if not raw and not update_fields:
    #     order_items = OrderItem.objects.filter(order=instance.order)
    #     instance.order.item_count = order_items.count()
    #     instance.order.save(update_fields=["item_count"])


@receiver(post_save, sender=Receive, dispatch_uid="receive_on_post_save")
def receive_on_post_save(sender, instance, raw, created, update_fields, **kwargs) -> None:
    if not raw and not update_fields:
        pass


@receiver(post_save, sender=ReceiveItem, dispatch_uid="update_receive_item_on_post_save")
def receive_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    if not raw and update_fields != ["added_to_stock"]:
        receive_items = ReceiveItem.objects.filter(receive=instance.receive)
        instance.receive.item_count = receive_items.count()
        instance.order_item.unit_qty_received = (
            instance.order_item.receiveitem_set.all().aggregate(unit_qty=Sum("unit_qty"))[
                "unit_qty"
            ]
        ) or Decimal(0.0)
        if instance.order_item.unit_qty_received == instance.order_item.unit_qty:
            instance.order_item.status = COMPLETE
        elif instance.order_item.unit_qty_received < instance.order_item.unit_qty:
            instance.order_item.status = PARTIAL
        instance.order_item.save()

        order = instance.receive.order
        unit_qty_received = OrderItem.objects.filter(order=order).aggregate(
            unit_qty_received=Sum("unit_qty_received")
        )["unit_qty_received"] or Decimal(0.0)
        unit_qty = OrderItem.objects.filter(order=order).aggregate(unit_qty=Sum("unit_qty"))[
            "unit_qty"
        ] or Decimal(0.0)
        if unit_qty_received == unit_qty:
            order.status = COMPLETE
            order.save()
        # add to stock
        for i in range(0, int(instance.qty)):
            Stock.objects.create(
                receive_item=instance,
                qty_in=1,
                qty_out=0,
                product=instance.order_item.product,
                container=instance.container,
                location=instance.receive.location,
                confirmed=False,
                label_configuration=instance.receive.label_configuration,
                lot=instance.lot,
            )


@receiver(post_save, sender=StockRequestItem, dispatch_uid="stock_request_item_on_post_save")
def stock_request_item_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock_request.item_count = StockRequestItem.objects.filter(
            stock_request=instance.stock_request
        ).count()
        instance.stock_request.save(update_fields=["item_count"])


@receiver(post_save, sender=RepackRequest, dispatch_uid="repack_request_on_post_save")
def repack_request_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        if not instance.processed:
            process_repack_request(instance)


@receiver(post_delete, sender=ReceiveItem, dispatch_uid="receive_item_on_post_delete")
def receive_item_on_post_delete(sender, instance, using, **kwargs) -> None:
    instance.order_item.unit_qty_received = (
        instance.order_item.unit_qty_received - instance.unit_qty
    )
    instance.order_item.save()


@receiver(post_delete, sender=Stock, dispatch_uid="stock_on_post_delete")
def stock_on_post_delete(sender, instance, using, **kwargs) -> None:
    pass


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
