from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from ..models import StockTransfer


def transfer_stock(
    stock_transfer: StockTransfer, stock_codes: list[str], username: str | None = None
):
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    stock_transfer_item_model_cls = django_apps.get_model("edc_pharmacy.stocktransferitem")
    transferred, skipped_codes = [], []
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=stock_code,
                allocation__isnull=False,
                confirmed=True,
                location=stock_transfer.from_location,
            )
        except ObjectDoesNotExist:
            skipped_codes.append(stock_code)
        else:
            stock_transfer_item_model_cls.objects.create(
                stock=stock,
                stock_transfer=stock_transfer,
                user_created=username,
                created=get_utcnow(),
            )
            stock.location = stock_transfer.to_location
            stock.save()
            transferred.append(stock_code)
