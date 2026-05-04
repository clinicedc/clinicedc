from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.utils import timezone

from ..constants import CENTRAL_LOCATION, TXN_TRANSFER_DISPATCHED
from ..exceptions import StockTransferError
from ..transaction_log import apply_transaction
from ..utils import is_dispensed

if TYPE_CHECKING:
    from ..models import Stock, StockTransfer, StockTransferItem


def transfer_stock_to_location(
    stock_transfer: StockTransfer, stock_codes: list[str], request: WSGIRequest = None
) -> tuple[list[str], list[str], list[str], list[str]]:
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    stock_transfer_item_model_cls: type[StockTransferItem] = django_apps.get_model(
        "edc_pharmacy.stocktransferitem"
    )
    transferred, dispensed_codes, skipped_codes, invalid_codes = ([], [], [], [])
    unprocessed_codes = copy(stock_codes)
    for stock_code in stock_codes:
        unprocessed_codes.remove(stock_code)
        if not stock_model_cls.objects.filter(code=stock_code).exists():
            invalid_codes.append(stock_code)
            continue
        # must be confirmed, allocated and at the "from" location
        opts = dict(
            code=stock_code,
            confirmation__isnull=False,
            allocation__registered_subject__isnull=False,
            location=stock_transfer.from_location,
        )
        with transaction.atomic():
            # Gate 2: stock must be allocated via a request whose destination is the
            # site being transferred to/from. Use StockRequestItem→StockRequest→location
            # rather than registered_subject.site, which can diverge in multi-site DBs.
            if stock_transfer.to_location.name == CENTRAL_LOCATION:
                opts.update(
                    allocation__registered_subject__site=stock_transfer.from_location.site,  # noqa:E501
                )
            else:
                opts.update(
                    allocation__registered_subject__site=stock_transfer.to_location.site,  # noqa:E501
                )
            try:
                stock_obj = stock_model_cls.objects.select_for_update(of=("self",)).get(**opts)
            except ObjectDoesNotExist:
                skipped_codes.append(stock_code)
            else:
                if stock_obj.dispensed:
                    dispensed_codes.append(stock_code)
                else:
                    stock_transfer_item = stock_transfer_item_model_cls.objects.create(
                        stock=stock_obj,
                        stock_transfer=stock_transfer,
                        user_created=request.user.username,
                        created=timezone.now(),
                    )
                    apply_transaction(
                        stock_obj,
                        TXN_TRANSFER_DISPATCHED,
                        request.user,
                        new_location_id=stock_transfer.to_location.id,
                        stock_transfer_item=stock_transfer_item,
                    )
                    transferred.append(stock_code)

                    if len(stock_codes) != (
                        len(unprocessed_codes)
                        + len(transferred)
                        + len(dispensed_codes)
                        + len(skipped_codes)
                        + len(invalid_codes)
                    ):
                        codes = transferred + dispensed_codes + skipped_codes + invalid_codes
                        suspect_codes = [c for c in stock_codes if c not in codes]
                        raise StockTransferError(
                            f"Some codes were not accounted for. Got {suspect_codes} "
                            "Cancelling transfer"
                        )
    return transferred, dispensed_codes, skipped_codes, invalid_codes


__all__ = ["transfer_stock_to_location"]
