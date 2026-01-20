from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.utils import timezone

from ..constants import CENTRAL_LOCATION
from ..exceptions import StockTransferError
from ..utils import is_dispensed

if TYPE_CHECKING:
    from ..models import (
        ConfirmationAtLocationItem,
        Stock,
        StockTransfer,
        StockTransferItem,
        StorageBinItem,
    )


def transfer_stock_to_location(
    stock_transfer: StockTransfer, stock_codes: list[str], request: WSGIRequest = None
) -> tuple[list[str], list[str], list[str], list[str]]:
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    stock_transfer_item_model_cls: type[StockTransferItem] = django_apps.get_model(
        "edc_pharmacy.stocktransferitem"
    )
    storage_bin_item_model_cls: type[StorageBinItem] = django_apps.get_model(
        "edc_pharmacy.storagebinitem"
    )
    confirmation_at_location_item_model_cls: type[ConfirmationAtLocationItem] = (
        django_apps.get_model("edc_pharmacy.confirmationatlocationitem")
    )
    transferred, dispensed_codes, skipped_codes, invalid_codes = [], [], [], []
    for stock_code in stock_codes:
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
        try:
            stock_model_cls.objects.get(**opts)
        except ObjectDoesNotExist:
            skipped_codes.append(stock_code)
        else:
            if stock_transfer.to_location.name == CENTRAL_LOCATION:
                opts.update(
                    allocation__registered_subject__site=stock_transfer.from_location.site,
                )
            else:
                opts.update(
                    allocation__registered_subject__site=stock_transfer.to_location.site
                )
            try:
                stock_obj = stock_model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                skipped_codes.append(stock_code)
            else:
                if is_dispensed(stock_code):
                    dispensed_codes.append(stock_code)
                else:
                    with transaction.atomic():
                        # get or create stock_transfer_item and relate
                        # to this stock transfer
                        stock_transfer_item_model_cls.objects.create(
                            stock=stock_obj,
                            stock_transfer=stock_transfer,
                            user_created=request.user.username,
                            created=timezone.now(),
                        )

                        # remove stock from the storage bin, if stored at
                        # a site bin
                        storage_bin_item_model_cls.objects.filter(stock=stock_obj).delete()
                        stock_obj.stored_at_location = False

                        # delete confirmation (you can still see it in history)
                        confirmation_at_location_item_model_cls.objects.filter(
                            stock=stock_obj
                        ).delete()

                        # change location of stock
                        stock_obj.location = stock_transfer.to_location

                        # save
                        stock_obj.save()

                        transferred.append(stock_code)

                        if len(stock_codes) != (
                            len(transferred)
                            + len(dispensed_codes)
                            + len(skipped_codes)
                            + len(invalid_codes)
                        ):
                            raise StockTransferError(
                                "Some codes were not accounted for. Cancelling transfer"
                            )
    return transferred, dispensed_codes, skipped_codes, invalid_codes


__all__ = ["transfer_stock_to_location"]
