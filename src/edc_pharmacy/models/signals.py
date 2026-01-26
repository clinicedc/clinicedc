from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from celery.states import PENDING
from clinicedc_constants import CANCEL, COMPLETE, NEW
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_utils.celery import get_task_result, run_task_sync_or_async

from ..constants import PARTIAL
from ..exceptions import InsufficientStockError
from ..model_mixins import StudyMedicationCrfModelMixin
from ..utils import (
    create_new_stock_on_receive,
    process_repack_request,
    update_previous_refill_end_datetime,
)
from .stock import (
    Allocation,
    Confirmation,
    ConfirmationAtLocationItem,
    DispenseItem,
    OrderItem,
    Receive,
    ReceiveItem,
    RepackRequest,
    Stock,
    StockAdjustment,
    StockRequest,
    StockRequestItem,
    StockTransferItem,
    StorageBinItem,
)

if TYPE_CHECKING:
    from .stock import Order


def update_order_status(order: Order):
    unit_qty_received = OrderItem.objects.filter(order=order).aggregate(
        unit_qty=Sum("unit_qty_received")
    )["unit_qty"] or Decimal("0.0")
    unit_qty_ordered = OrderItem.objects.filter(order=order).aggregate(
        unit_qty=Sum("unit_qty_ordered")
    )["unit_qty"] or Decimal("0.0")
    if unit_qty_received is None or unit_qty_received == Decimal("0.0"):
        order.status = NEW
    elif unit_qty_received == unit_qty_ordered:
        order.status = COMPLETE
    elif unit_qty_received > Decimal("0.0"):
        order.status = PARTIAL
    order.save(update_fields=["status"])
    order.refresh_from_db()


def update_orderitem_status(order_item: OrderItem):
    if order_item.unit_qty_received == Decimal("0.0"):
        order_item.status = NEW
    elif order_item.unit_qty_received == order_item.unit_qty_ordered:
        order_item.status = COMPLETE
    else:
        order_item.status = PARTIAL
    order_item.save(update_fields=["status"])
    order_item.refresh_from_db()


@receiver(post_save, sender=Confirmation, dispatch_uid="confirmation_on_post_save")
def confirmation_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update confirmed"""
    if not raw and not update_fields:
        instance.stock.confirmed = True
        instance.stock.save(update_fields=["confirmed"])


@receiver(post_save, sender=Stock, dispatch_uid="stock_on_post_save")
def stock_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update unit qty and other columns"""
    pass


@receiver(
    post_save,
    sender=StockAdjustment,
    dispatch_uid="stock_adjustment_on_post_save",
)
def stock_adjustment_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update unit qty"""
    if not raw and not update_fields:
        instance.stock.unit_qty_in = instance.unit_qty_in_new
        if instance.stock.unit_qty_out > instance.stock.unit_qty_in:
            raise InsufficientStockError(
                "Invalid adjustment. Expected a value greater than or equal to "
                f"{instance.stock.unit_qty_out}. See {instance}."
            )
        instance.stock.save(update_fields=["unit_qty_in"])


@receiver(post_save, sender=OrderItem, dispatch_uid="order_item_on_post_save")
def order_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    if not raw and not update_fields:
        # recalculate unit_qty_pending
        instance.unit_qty_ordered = instance.item_qty_ordered * instance.container_unit_qty
        instance.unit_qty_pending = instance.unit_qty_ordered - (
            instance.unit_qty_received or Decimal("0.0")
        )
        instance.save(update_fields=["unit_qty_pending", "unit_qty_ordered"])
        instance.refresh_from_db()
        update_orderitem_status(order_item=instance)
        update_order_status(order=instance.order)


@receiver(post_save, sender=Receive, dispatch_uid="receive_on_post_save")
def receive_on_post_save(sender, instance, raw, created, update_fields, **kwargs) -> None:
    if not raw and not update_fields:
        pass


@receiver(post_save, sender=ReceiveItem, dispatch_uid="receive_item_on_post_save")
def receive_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    if not raw and update_fields in (["added_to_stock"], ["container_unit_qty"]):
        # update receive item_count after receive_item
        receive_items = ReceiveItem.objects.filter(receive=instance.receive)
        instance.receive.item_count = receive_items.count()
        instance.receive.save(update_fields=["item_count"])

        # update order_item after receive_item
        instance.order_item.unit_qty_received = (
            instance.order_item.receiveitem_set.all().aggregate(
                unit_qty=Sum("unit_qty_received")
            )["unit_qty"]
        ) or Decimal("0.0")

        instance.order_item.save(update_fields=["unit_qty_received"])

        update_orderitem_status(order_item=instance.order_item)

        # update order status
        update_order_status(order=instance.order_item.order)

        # add to stock
        create_new_stock_on_receive(receive_item_pk=instance.id)


@receiver(post_save, sender=StockRequest, dispatch_uid="stock_request_on_post_save")
def stock_request_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        if instance.cancel == CANCEL:
            if not Allocation.objects.filter(
                stock_request_item__stock_request=instance
            ).exists():
                instance.stockrequestitem_set.all().delete()
            else:
                instance.cancel = ""
                instance.save(update_fields=["cancel"])
        instance.item_count = instance.stockrequestitem_set.count()
        instance.save(update_fields=["item_count"])


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
        result = get_task_result(instance)
        if getattr(result, "state", "") == PENDING:
            pass
        else:
            task = run_task_sync_or_async(
                process_repack_request,
                repack_request_id=str(instance.id),
                username=instance.user_modified or instance.user_created,
            )
            instance.task_id = getattr(task, "id", None)
            instance.save(update_fields=["task_id"])


@receiver(
    post_save,
    sender=Allocation,
    dispatch_uid="allocation_on_post_save",
)
def allocation_on_post_save(sender, instance, raw, created, update_fields, **kwargs) -> None:
    stock = Stock.objects.get(code=instance.code)
    stock.subject_identifier = instance.registered_subject.subject_identifier
    stock.save(update_fields=["subject_identifier"])


@receiver(
    post_save,
    sender=StockTransferItem,
    dispatch_uid="stock_transfer_item_on_post_save",
)
def stock_transfer_item_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock.in_transit = True
        instance.stock.save(update_fields=["in_transit"])


@receiver(
    post_save,
    sender=ConfirmationAtLocationItem,
    dispatch_uid="confirm_at_location_item_on_post_save",
)
def confirm_at_location_item_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock.confirmed_at_location = True
        instance.stock.save(update_fields=["confirmed_at_location"])


@receiver(
    post_save,
    sender=StorageBinItem,
    dispatch_uid="storage_bin_item_on_post_save",
)
def storage_bin_item_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock.stored_at_location = True
        instance.stock.save(update_fields=["stored_at_location"])


@receiver(
    post_save,
    sender=DispenseItem,
    dispatch_uid="dispense_item_on_post_save",
)
def dispense_item_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock.dispensed = True
        instance.stock.qty_out = 1
        instance.stock.unit_qty_out = instance.stock.container_unit_qty * 1
        instance.stock.save(update_fields=["dispensed", "qty_out", "unit_qty_out"])
        StorageBinItem.objects.filter(stock=instance.stock).delete()


@receiver(post_delete, sender=Confirmation, dispatch_uid="confirmation_on_post_delete")
def confirmation_on_post_delete(ender, instance, using, **kwargs):
    """Update confirmed"""
    instance.stock.confirmed = False
    instance.stock.save(update_fields=["confirmed"])


@receiver(post_delete, sender=ReceiveItem, dispatch_uid="receive_item_on_post_delete")
def receive_item_on_post_delete(sender, instance, using, **kwargs) -> None:
    instance.order_item.unit_qty_received = (
        instance.order_item.unit_qty_received - instance.unit_qty_received
    )
    instance.order_item.save()


@receiver(post_delete, sender=Stock, dispatch_uid="stock_on_post_delete")
def stock_on_post_delete(sender, instance, using, **kwargs) -> None:
    if getattr(instance, "confirmation", None):
        instance.confirm.delete()


@receiver(
    post_delete,
    sender=Allocation,
    dispatch_uid="allocation_post_delete",
)
def allocation_post_delete(sender, instance, using, **kwargs) -> None:
    if getattr(instance, "stock", None):
        instance.stock.subject_identifier = None
        instance.stock.save(update_fields=["subject_identifier"])


@receiver(
    post_delete,
    sender=StockTransferItem,
    dispatch_uid="stock_transfer_item_post_delete",
)
def stock_transfer_item_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.in_transit = False
    instance.stock.save(update_fields=["in_transit"])


@receiver(
    post_delete,
    sender=ConfirmationAtLocationItem,
    dispatch_uid="confirm_at_location_item_post_delete",
)
def confirm_at_location_item_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.confirmed_at_location = False
    instance.stock.save(update_fields=["confirmed_at_location"])


@receiver(
    post_delete,
    sender=StorageBinItem,
    dispatch_uid="storage_bin_item_post_delete",
)
def storage_bin_item_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.stored_at_location = False
    instance.stock.save(update_fields=["stored_at_location"])


@receiver(
    post_delete,
    sender=DispenseItem,
    dispatch_uid="dispense_item_on_post_delete",
)
def dispense_item_on_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.dispensed = False
    instance.stock.qty_out = 0
    instance.stock.unit_qty_out = 0
    instance.stock.save(update_fields=["dispensed", "qty_out", "unit_qty_out"])


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
    if not raw and not update_fields and isinstance(instance, (StudyMedicationCrfModelMixin,)):
        update_previous_refill_end_datetime(instance)
