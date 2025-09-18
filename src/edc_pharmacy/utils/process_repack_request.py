from __future__ import annotations

from uuid import UUID

from celery import shared_task
from django.apps import apps as django_apps
from django.utils import timezone

from ..exceptions import InsufficientStockError, RepackError


@shared_task
def process_repack_request(repack_request_id: UUID | None = None, username: str | None = None):
    """Take from stock and fill container as new stock item."""
    repack_request_model_cls = django_apps.get_model("edc_pharmacy.repackrequest")
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    repack_request = repack_request_model_cls.objects.get(id=repack_request_id)
    repack_request.task_id = None
    repack_request.processed_qty = repack_request.processed_qty = (
        stock_model_cls.objects.filter(repack_request=repack_request).count()
    )
    repack_request.requested_qty = (
        repack_request.processed_qty
        if not repack_request.requested_qty
        else repack_request.requested_qty
    )
    number_to_process = repack_request.requested_qty - repack_request.processed_qty
    if not getattr(repack_request.from_stock, "confirmation", None):
        raise RepackError("Source stock item not confirmed")
    stock_model_cls = repack_request.from_stock.__class__
    for _ in range(0, int(number_to_process)):
        try:
            stock_model_cls.objects.create(
                receive_item=None,
                qty_in=1,
                qty_out=0,
                qty=1,
                from_stock=repack_request.from_stock,
                container=repack_request.container,
                location=repack_request.from_stock.location,
                repack_request=repack_request,
                lot=repack_request.from_stock.lot,
                user_created=username,
                created=timezone.now(),
            )
        except InsufficientStockError:
            break
    repack_request.processed_qty = stock_model_cls.objects.filter(
        repack_request=repack_request
    ).count()
    repack_request.user_modified = username
    repack_request.modified = timezone.now()
    repack_request.save(
        update_fields=[
            "requested_qty",
            "processed_qty",
            "task_id",
            "user_modified",
            "modified",
        ]
    )
    repack_request.refresh_from_db()


__all__ = ["process_repack_request"]
