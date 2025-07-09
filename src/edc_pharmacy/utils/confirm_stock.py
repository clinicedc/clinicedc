from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from ..models import Confirmation, Receive, RepackRequest, Stock


def confirm_stock(
    obj: RepackRequest | Receive | None,
    stock_codes: list[str],
    fk_attr: str | None = None,
    confirmed_by: str | None = None,
    user_created: str = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes
    and a request/receive pk.

    Called from ConfirmStock view.

    See also: confirm_stock_action
    """
    stock_model_cls: Type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    confirmation_model_cls: Type[Confirmation] = django_apps.get_model(
        "edc_pharmacy.confirmation"
    )
    stock_codes = [s.strip() for s in stock_codes]
    invalid = []
    confirmed = []
    already_confirmed = []
    opts = {}
    if obj:
        opts = {fk_attr: obj.id}
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(code=stock_code, **opts)
        except ObjectDoesNotExist:
            invalid.append(stock_code)
        else:
            try:
                confirmation_model_cls.objects.get(stock=stock)
            except ObjectDoesNotExist:
                confirmation_model_cls.objects.create(
                    stock=stock,
                    confirmed_datetime=get_utcnow(),
                    confirmed_by=confirmed_by or user_created,
                )
                confirmed.append(stock.code)
            else:
                already_confirmed.append(stock.code)
    return confirmed, already_confirmed, invalid


__all__ = ["confirm_stock"]
