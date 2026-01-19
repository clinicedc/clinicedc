from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .get_related_or_none import get_related_or_none

if TYPE_CHECKING:
    from ..models import Stock


def is_dispensed(stock: Stock | str) -> bool | None:
    if isinstance(stock, str):
        stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
        try:
            stock = stock_model_cls.objects.get(code=stock)
        except ObjectDoesNotExist:
            stock = None
    if (
        stock
        and get_related_or_none(stock, "confirmation")
        and get_related_or_none(stock, "from_stock")
    ):
        return bool(get_related_or_none(stock, "dispenseitem"))
    return None
