from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from edc_utils import get_utcnow

from ..exceptions import ConfirmAtSiteError

if TYPE_CHECKING:
    from uuid import UUID

    from ..models import (
        ConfirmationAtSite,
        ConfirmationAtSiteItem,
        Location,
        Stock,
        StockTransfer,
    )


def confirm_stock_at_site(
    stock_transfer: StockTransfer,
    stock_codes: list[str],
    location: UUID,
    request: WSGIRequest = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes
    and a request/receive pk.

    Called from ConfirmStock view.

    See also: confirm_stock_action
    """
    confirmed_by = request.user.username
    stock_model_cls: Type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    confirmation_at_site_model_cls: Type[ConfirmationAtSite] = django_apps.get_model(
        "edc_pharmacy.confirmationatsite"
    )
    confirmation_at_site_item_model_cls: Type[ConfirmationAtSiteItem] = django_apps.get_model(
        "edc_pharmacy.confirmationatsiteitem"
    )
    location_model_cls: Type[Location] = django_apps.get_model("edc_pharmacy.location")

    location = location_model_cls.objects.get(pk=location)

    confirmation_at_site, _ = confirmation_at_site_model_cls.objects.get_or_create(
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
                    confirmation__isnull=False,
                    allocation__isnull=False,
                    confirmationatsiteitem__isnull=True,
                )
            except ObjectDoesNotExist:
                already_confirmed.append(stock_code)
            else:
                obj = confirmation_at_site_item_model_cls(
                    confirmation_at_site=confirmation_at_site,
                    stock=stock,
                    confirmed_datetime=get_utcnow(),
                    confirmed_by=confirmed_by,
                    user_created=confirmed_by,
                    created=get_utcnow(),
                )
                try:
                    obj.save()
                except ConfirmAtSiteError as e:
                    messages.add_message(request, messages.ERROR, str(e))
                    invalid.append(stock_code)
                else:
                    confirmed.append(stock_code)
    return confirmed, already_confirmed, invalid


__all__ = ["confirm_stock_at_site"]
