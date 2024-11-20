from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from ..models import Receive, RepackRequest


def confirm_stock(
    obj: RepackRequest | Receive | None,
    stock_codes: list[str],
    fk_attr: str | None,
    confirmed_by: str | None = None,
    user_created: str = None,
    created: datetime = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes
    and a request/receive pk.

    Called from ConfirmStock view.

    See also: confirm_stock_action
    """
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    stock_codes = [s.strip() for s in stock_codes]
    invalid = []
    confirmed = []
    already_confirmed = []
    opts = {}
    if obj:
        opts = {fk_attr: obj.id}
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=stock_code,
                **opts,
            )
        except ObjectDoesNotExist:
            invalid.append(stock_code)
        else:
            if not stock.confirmed:
                stock.confirmed = True
                stock.user_modified = user_created
                stock.modified = created
                stock.confirmed_datetime = get_utcnow()
                stock.confirmed_by = confirmed_by or user_created
                stock.save(
                    update_fields=[
                        "confirmed",
                        "confirmed_datetime",
                        "confirmed_by",
                        "user_modified",
                        "modified",
                    ]
                )
                confirmed.append(stock.code)
            else:
                already_confirmed.append(stock.code)
    return confirmed, already_confirmed, invalid
