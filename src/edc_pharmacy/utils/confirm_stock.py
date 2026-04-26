from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.utils import timezone

from ..constants import TXN_RECEIVED
from ..exceptions import InvalidTransitionError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from ..models import Receive, RepackRequest, Stock


def confirm_stock(
    obj: RepackRequest | Receive | None,
    stock_codes: list[str],
    fk_attr: str | None = None,
    confirmed_by: str | None = None,
    user_created: str | None = None,
    actor: AbstractUser | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Confirm stock instances given a list of stock codes.

    Called from ConfirmStock view and confirm_stock_action.
    Each code is processed independently (per-scan atomicity).
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    stock_codes = [s.strip() for s in stock_codes]
    confirmed = []
    already_confirmed = []
    invalid = []
    opts = {fk_attr: obj.id} if obj and fk_attr else {}
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(code=stock_code, **opts)
        except stock_model_cls.DoesNotExist:
            invalid.append(stock_code)
        else:
            try:
                apply_transaction(
                    stock,
                    TXN_RECEIVED,
                    actor,
                    confirmed_datetime=timezone.now(),
                    confirmed_by=confirmed_by or user_created or "",
                )
            except InvalidTransitionError:
                already_confirmed.append(stock_code)
            else:
                confirmed.append(stock.code)
    return confirmed, already_confirmed, invalid


__all__ = ["confirm_stock"]
