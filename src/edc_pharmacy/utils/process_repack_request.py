from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from celery import shared_task
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from ..constants import TXN_REPACK_CONSUMED, TXN_REPACK_PRODUCED
from ..exceptions import RepackError
from ..transaction_log import apply_transaction


@shared_task
def process_repack_request(repack_request_id: UUID | None = None, username: str | None = None):
    """Repack bulk stock into patient bottles.

    Creates child Stock rows from the bulk ``from_stock`` and writes
    TXN_REPACK_PRODUCED on each child and a single TXN_REPACK_CONSUMED on
    the bulk stock covering the total units drawn.
    """
    repack_request_model_cls = django_apps.get_model("edc_pharmacy.repackrequest")
    repack_request = repack_request_model_cls.objects.get(id=repack_request_id)

    if not getattr(repack_request.from_stock, "confirmation", None):
        raise RepackError("Source stock item not confirmed")

    stock_model_cls = repack_request.from_stock.__class__
    repack_request.task_id = None
    repack_request.item_qty_processed = stock_model_cls.objects.filter(
        repack_request=repack_request
    ).count()
    repack_request.item_qty_repack = (
        repack_request.item_qty_processed
        if not repack_request.item_qty_repack
        else repack_request.item_qty_repack
    )
    item_qty_to_process = repack_request.item_qty_repack - repack_request.item_qty_processed

    actor = None
    if username:
        User = get_user_model()
        try:
            actor = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

    from_stock = repack_request.from_stock
    total_consumed = Decimal("0")

    with transaction.atomic():
        for _ in range(int(item_qty_to_process)):
            available = (
                (from_stock.unit_qty_in or Decimal("0"))
                - (from_stock.unit_qty_out or Decimal("0"))
                - total_consumed
            )
            if available < repack_request.container_unit_qty:
                break
            child = stock_model_cls.objects.create(
                receive_item=None,
                qty_in=1,
                qty_out=0,
                qty=1,
                unit_qty_in=repack_request.container_unit_qty,
                unit_qty_out=Decimal("0.0"),
                from_stock=from_stock,
                container=repack_request.container,
                container_unit_qty=repack_request.container_unit_qty,
                location=from_stock.location,
                repack_request=repack_request,
                lot=from_stock.lot,
                user_created=username,
                created=timezone.now(),
            )
            apply_transaction(child, TXN_REPACK_PRODUCED, actor, repack_request=repack_request)
            repack_request.item_qty_processed += 1
            repack_request.unit_qty_processed += repack_request.container_unit_qty
            total_consumed += repack_request.container_unit_qty

        if total_consumed > 0:
            apply_transaction(
                from_stock,
                TXN_REPACK_CONSUMED,
                actor,
                qty_delta=Decimal("0"),
                unit_qty_delta=-total_consumed,
                repack_request=repack_request,
            )

        repack_request.user_modified = username
        repack_request.modified = timezone.now()
        repack_request.save(
            update_fields=[
                "item_qty_repack",
                "item_qty_processed",
                "unit_qty_processed",
                "task_id",
                "user_modified",
                "modified",
            ]
        )
        repack_request.refresh_from_db()


__all__ = ["process_repack_request"]
