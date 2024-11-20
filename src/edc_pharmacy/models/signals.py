from decimal import Decimal

from celery.states import PENDING
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, PARTIAL
from edc_utils.celery import get_task_result, run_task_sync_or_async

from ..exceptions import InsufficientStockError
from ..model_mixins import StudyMedicationCrfModelMixin
from ..tasks import process_repack_request
from ..utils import update_previous_refill_end_datetime
from .stock import (
    Allocation,
    DispenseItem,
    OrderItem,
    Receive,
    ReceiveItem,
    RepackRequest,
    Stock,
    StockRequest,
    StockRequestItem,
    StockTransferConfirmation,
)


@receiver(post_save, sender=Stock, dispatch_uid="update_stock_on_post_save")
def stock_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Update unit qty"""
    if not raw and not update_fields:
        instance.unit_qty_in = Decimal(instance.qty_in) * Decimal(instance.container.qty)
        instance.unit_qty_out = Decimal(
            sender.objects.filter(from_stock=instance).count()
        ) * Decimal(instance.container.qty)
        if (
            instance.from_stock
            and instance.from_stock.unit_qty_out > instance.from_stock.unit_qty_in
        ):
            raise InsufficientStockError("Unit QTY OUT cannot exceed Unit QTY IN.")
        elif (
            instance.from_stock
            and instance.from_stock.unit_qty_out == instance.from_stock.unit_qty_in
        ):
            instance.qty_out = 1
            instance.qty = 0
        instance.save(update_fields=["unit_qty_in", "unit_qty_out", "qty"])


@receiver(post_save, sender=OrderItem, dispatch_uid="update_order_item_on_post_save")
def order_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    if not raw and not update_fields:
        # recalculate unit_qty
        unit_qty_ordered = instance.qty * instance.container.qty
        instance.unit_qty = unit_qty_ordered - (instance.unit_qty_received or Decimal(0))
        instance.save(update_fields=["unit_qty"])


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
                receive_item_id=instance.id,
                qty_in=1,
                qty_out=0,
                qty=1,
                product_id=instance.order_item.product.id,
                container_id=instance.container.id,
                location_id=instance.receive.location.id,
                confirmed=False,
                lot_id=instance.lot.id,
            )


@receiver(post_save, sender=StockRequest, dispatch_uid="stock_request_on_post_save")
def stock_request_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        if instance.cancel == "CANCEL":
            if not Allocation.objects.filter(
                stock_request_item__stock_request=instance
            ).exists():
                instance.stockrequestitem_set.all().delete()
            else:
                instance.cancel = ""
                instance.save(update_fields=["cancel"])


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
    sender=StockTransferConfirmation,
    dispatch_uid="stock_transfer_confirmation_on_post_save",
)
def stock_transfer_confirmation_on_post_save(
    sender, instance, raw, created, update_fields, **kwargs
) -> None:
    if not raw and not update_fields:
        instance.stock.confirmed_at_site = True
        instance.stock.save(update_fields=["confirmed_at_site"])


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
        instance.stock.unit_qty_out = instance.stock.container.qty * 1
        instance.stock.save(update_fields=["qty_out", "unit_qty_out", "dispensed"])


@receiver(post_delete, sender=ReceiveItem, dispatch_uid="receive_item_on_post_delete")
def receive_item_on_post_delete(sender, instance, using, **kwargs) -> None:
    instance.order_item.unit_qty_received = (
        instance.order_item.unit_qty_received - instance.unit_qty
    )
    instance.order_item.save()


@receiver(post_delete, sender=Stock, dispatch_uid="stock_on_post_delete")
def stock_on_post_delete(sender, instance, using, **kwargs) -> None:
    pass


@receiver(
    post_delete,
    sender=StockTransferConfirmation,
    dispatch_uid="stock_transfer_confirmation_post_delete",
)
def stock_transfer_confirmation_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.confirmed_at_site = False
    instance.stock.save(update_fields=["confirmed_at_site"])


@receiver(
    post_delete,
    sender=DispenseItem,
    dispatch_uid="dispense_item_on_post_delete",
)
def dispense_item_on_post_delete(sender, instance, using, **kwargs) -> None:
    instance.stock.dispensed = False
    instance.stock.qty_out = 0
    instance.stock.unit_qty_out = 0
    instance.stock.save(update_fields=["qty_out", "unit_qty_out", "dispensed"])


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
