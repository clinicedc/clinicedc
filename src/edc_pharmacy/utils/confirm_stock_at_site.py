from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from uuid import UUID

    from ..models import Location, Stock, StockTransferConfirmation


def confirm_stock_at_site(
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
    stock_transfer_confirmation_model_cls: Type[StockTransferConfirmation] = (
        django_apps.get_model("edc_pharmacy.stocktransferconfirmation")
    )
    location_model_cls: Type[Location] = django_apps.get_model("edc_pharmacy.location")
    confirmed, already_confirmed, invalid = [], [], []
    stock_codes = [s.strip() for s in stock_codes]
    location = location_model_cls.objects.get(pk=location)
    for stock_code in stock_codes:
        if not stock_model_cls.objects.filter(code=stock_code).exists():
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
                obj = stock_transfer_confirmation_model_cls.objects.create(
                    stock=stock,
                    confirmed_datetime=get_utcnow(),
                    confirmed_by=confirmed_by,
                    user_created=confirmed_by,
                    created=get_utcnow(),
                )
                obj.save()
                confirmed.append(stock_code)
    return confirmed, already_confirmed, invalid
