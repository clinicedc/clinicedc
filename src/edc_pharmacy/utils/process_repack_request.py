from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from celery import shared_task
from django.apps import apps as django_apps
from django.db import transaction
from django.utils import timezone

from ..exceptions import InsufficientStockError, RepackError


@shared_task
def process_repack_request(repack_request_id: UUID | None = None, username: str | None = None):
    """Take from stock and fill container as new stock item."""
    repack_request_model_cls = django_apps.get_model("edc_pharmacy.repackrequest")
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    repack_request = repack_request_model_cls.objects.get(id=repack_request_id)
    repack_request.task_id = None
    repack_request.item_qty_processed = repack_request.item_qty_processed = (
        stock_model_cls.objects.filter(repack_request=repack_request).count()
    )
    repack_request.item_qty_repack = (
        repack_request.item_qty_processed
        if not repack_request.item_qty_repack
        else repack_request.item_qty_repack
    )
    item_qty_to_process = repack_request.item_qty_repack - repack_request.item_qty_processed
    if not getattr(repack_request.from_stock, "confirmation", None):
        raise RepackError("Source stock item not confirmed")
    stock_model_cls = repack_request.from_stock.__class__
    with transaction.atomic():
        for _ in range(0, int(item_qty_to_process)):
            try:
                stock_model_cls.objects.create(
                    receive_item=None,
                    qty_in=1,
                    qty_out=0,
                    qty=1,
                    unit_qty_in=repack_request.container_unit_qty,
                    unit_qty_out=Decimal("0.0"),
                    from_stock=repack_request.from_stock,
                    container=repack_request.container,
                    container_unit_qty=repack_request.container_unit_qty,
                    location=repack_request.from_stock.location,
                    repack_request=repack_request,
                    lot=repack_request.from_stock.lot,
                    user_created=username,
                    created=timezone.now(),
                )
            except InsufficientStockError:
                break
            else:
                repack_request.item_qty_processed += 1
                repack_request.unit_qty_processed += repack_request.container_unit_qty
                repack_request.from_stock.unit_qty_out += repack_request.container_unit_qty
        repack_request.from_stock.user_modified = username
        repack_request.from_stock.save(update_fields=["unit_qty_out", "user_modified"])
        repack_request.from_stock.refresh_from_db()
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
        # repack_request.from_stock.unit_qty_out = (
        #     repack_request.from_stock.unit_qty_out + repack_request.unit_qty_processed
        # )
        #
        # repack_request.from_stock.save(update_fields=["unit_qty_out"])


__all__ = ["process_repack_request"]
