from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.utils import timezone

from ..constants import TXN_TRANSFER_RECEIVED
from ..exceptions import ConfirmAtLocationError, InvalidTransitionError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from uuid import UUID

    from ..models import (
        ConfirmationAtLocation,
        Location,
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

    Returns ``(confirmed, already_confirmed, invalid)``.
    Bucketing happens in-loop so a TOCTOU race (a code confirmed by a
    concurrent request between an upfront pre-check and our select_for_update)
    is correctly reported as ``already_confirmed`` rather than ``invalid``.
    """
    confirmed_by = request.user.username
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

    for stock_code in stock_codes:
        with transaction.atomic():
            try:
                stock_transfer_item = stock_transfer_item_model_cls.objects.select_for_update(
                    of=("self", "stock")
                ).get(stock__code=stock_code, stock_transfer=stock_transfer)
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
                continue
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
            except InvalidTransitionError:
                # Stock state forbids TXN_TRANSFER_RECEIVED — typically
                # because confirmed_at_location is already True (this code
                # was already received, possibly by a concurrent scan).
                already_confirmed_codes.append(stock_code)
            except ConfirmAtLocationError as e:
                # Domain guard failure (e.g. site/transfer mismatch). This
                # is a genuinely invalid scan, not an already-confirmed one.
                if request:
                    messages.add_message(request, messages.ERROR, str(e))
                invalid_codes.append(stock_code)
            else:
                confirmed_codes.append(stock_code)
    return confirmed_codes, already_confirmed_codes, invalid_codes


__all__ = ["confirm_stock_at_location"]
