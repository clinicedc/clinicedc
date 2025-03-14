from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from uuid import UUID

    from ..models import (
        Location,
        Stock,
        StockTransfer,
        StockTransferConfirmation,
        StockTransferConfirmationItem,
    )


def confirm_stock_at_site(
    stock_transfer: StockTransfer,
    stock_codes: list[str],
    location: UUID,
    confirmed_by: str | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes
    and a request/receive pk.

    Called from ConfirmStock view.

    See also: confirm_stock_action
    """
    stock_model_cls: Type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    transfer_confirmation_model_cls: Type[StockTransferConfirmation] = django_apps.get_model(
        "edc_pharmacy.stocktransferconfirmation"
    )
    transfer_confirmation_item_model_cls: Type[StockTransferConfirmationItem] = (
        django_apps.get_model("edc_pharmacy.stocktransferconfirmationitem")
    )
    location_model_cls: Type[Location] = django_apps.get_model("edc_pharmacy.location")

    location = location_model_cls.objects.get(pk=location)
    transfer_confirmation, _ = transfer_confirmation_model_cls.objects.get_or_create(
        stock_transfer=stock_transfer,
        location=location,
    )

    confirmed, already_confirmed, invalid = [], [], []
    stock_codes = [s.strip() for s in stock_codes]
    for stock_code in stock_codes:
        if not stock_model_cls.objects.filter(code=stock_code).exists():
            invalid.append(stock_code)
        elif not stock_transfer.stocktransferitem_set.filter(stock__code=stock_code).exists():
            invalid.append(stock_code)
        else:
            try:
                stock = stock_model_cls.objects.get(
                    code=stock_code,
                    location=location,
                    confirmed=True,
                    allocation__isnull=False,
                    confirmed_at_site=False,
                )
            except ObjectDoesNotExist:
                already_confirmed.append(stock_code)
            else:
                obj = transfer_confirmation_item_model_cls(
                    stock_transfer_confirmation=transfer_confirmation,
                    stock=stock,
                    confirmed_datetime=get_utcnow(),
                    confirmed_by=confirmed_by,
                    user_created=confirmed_by,
                    created=get_utcnow(),
                )
                obj.save()
                confirmed.append(stock_code)
    return confirmed, already_confirmed, invalid


__all__ = ["confirm_stock_at_site"]
