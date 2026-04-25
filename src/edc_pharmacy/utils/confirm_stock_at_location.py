from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone

from ..constants import TXN_TRANSFER_RECEIVED
from ..exceptions import ConfirmAtLocationError, InvalidTransitionError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from uuid import UUID

    from ..models import (
        ConfirmationAtLocation,
        Location,
        Stock,
        StockTransfer,
        StockTransferItem,
    )


def confirm_stock_at_location(
    stock_transfer: StockTransfer,
    stock_codes: list[str],
    location: UUID,
    request: WSGIRequest | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes and a stock transfer.

    Called from ConfirmStock view.
    Each code is processed independently (per-scan atomicity).
    """
    confirmed_by = request.user.username
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    stock_transfer_item_model_cls: type[StockTransferItem] = django_apps.get_model(
        "edc_pharmacy.stocktransferitem"
    )
    confirm_at_location_model_cls: type[ConfirmationAtLocation] = django_apps.get_model(
        "edc_pharmacy.confirmationatlocation"
    )
    location_model_cls: type[Location] = django_apps.get_model("edc_pharmacy.location")

    location_obj = location_model_cls.objects.get(pk=location)
    confirm_at_location, _ = confirm_at_location_model_cls.objects.get_or_create(
        stock_transfer=stock_transfer,
        location=location_obj,
    )

    confirmed_codes, already_confirmed_codes, invalid_codes = [], [], []

    stock_codes = [s.strip() for s in stock_codes]
    valid_codes = [obj.code for obj in stock_model_cls.objects.filter(code__in=stock_codes)]
    invalid_codes = [c for c in stock_codes if c not in valid_codes]
    already_confirmed_codes = [
        obj.code
        for obj in stock_model_cls.objects.filter(
            stocktransferitem__stock_transfer=stock_transfer,
            stocktransferitem__confirmationatlocationitem__isnull=False,
        )
        if obj.code in valid_codes
    ]
    for stock_code in [c for c in valid_codes if c not in already_confirmed_codes]:
        try:
            stock_transfer_item = stock_transfer_item_model_cls.objects.get(
                stock__code=stock_code, stock_transfer=stock_transfer
            )
        except ObjectDoesNotExist:
            if request:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        f"{stock_code} not found in Stock Transfer "
                        f"{stock_transfer.transfer_identifier}."
                    ),
                )
            invalid_codes.append(stock_code)
        else:
            try:
                apply_transaction(
                    stock_transfer_item.stock,
                    TXN_TRANSFER_RECEIVED,
                    request.user,
                    site_location_id=location_obj.pk,
                    confirm_at_location=confirm_at_location,
                    stock_transfer_item=stock_transfer_item,
                    confirmed_datetime=timezone.now(),
                    confirmed_by=confirmed_by,
                )
            except (InvalidTransitionError, ConfirmAtLocationError) as e:
                if request:
                    messages.add_message(request, messages.ERROR, str(e))
                invalid_codes.append(stock_code)
            else:
                confirmed_codes.append(stock_code)
    return confirmed_codes, already_confirmed_codes, invalid_codes


__all__ = ["confirm_stock_at_location"]
