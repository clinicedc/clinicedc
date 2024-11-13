from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest

from edc_pharmacy.exceptions import RepackError

if TYPE_CHECKING:
    from ..models import RepackRequest


def process_repack_request(
    repack_request: RepackRequest | None = None, request: WSGIRequest | None = None
) -> RepackRequest:
    """Take from stock and fill container as new stock item.

    Do not change location here.
    """

    if repack_request.from_stock and not repack_request.processed:
        if not repack_request.from_stock.confirmed:
            raise RepackError("Stock not confirmed")
        stock_model_cls = repack_request.from_stock.__class__
        for index in range(0, int(repack_request.qty)):
            stock_model_cls.objects.create(
                receive_item=None,
                qty_in=1,
                from_stock=repack_request.from_stock,
                container=repack_request.container,
                location=repack_request.from_stock.location,
                repack_request=repack_request,
                confirmed=False,
                lot=repack_request.from_stock.lot,
            )
        repack_request.processed = True
        repack_request.save()
        if request:
            messages.add_message(
                request,
                messages.SUCCESS,
                (
                    "Repack request submitted. Next, print labels and label the stock. "
                    "Once all stock is labelled, go back to Repack and scan in the "
                    "labels to confirm the stock"
                ),
            )
    return repack_request
