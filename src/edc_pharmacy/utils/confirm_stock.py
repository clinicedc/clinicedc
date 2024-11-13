from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from ..models import Receive, RepackRequest


def confirm_stock(
    obj: RepackRequest | Receive,
    stock_codes: list[str],
    fk_attr: str,
    confirmed_by: str | None = None,
) -> tuple[int, int]:
    """Confirm stock instances given a list of stock codes
    and a request/receive pk.

    Called from ConfirmStock view.

    See also: confirm_stock_action
    """
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    confirmed, not_confirmed = 0, 0
    stock_codes = [s.strip() for s in stock_codes]
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=stock_code,
                confirmed=False,
                **{fk_attr: obj.id},
            )
        except ObjectDoesNotExist:
            not_confirmed += 1
        else:
            stock.confirmed = True
            stock.confirmed_datetime = get_utcnow()
            if confirmed_by:
                stock.confirmed_by = confirmed_by
                stock.save(update_fields=["confirmed", "confirmed_by"])
            else:
                stock.save(update_fields=["confirmed"])
            confirmed += 1
    return confirmed, not_confirmed
