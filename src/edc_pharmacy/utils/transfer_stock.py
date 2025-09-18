from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from ..models import StockTransfer


def transfer_stock(
    stock_transfer: StockTransfer, stock_codes: list[str], request: WSGIRequest = None
) -> tuple[list[str], list[str], list[str]]:
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    stock_transfer_item_model_cls = django_apps.get_model("edc_pharmacy.stocktransferitem")
    transferred, skipped_codes, invalid_codes = [], [], []
    for stock_code in stock_codes:
        try:
            stock = stock_model_cls.objects.get(
                code=stock_code,
                confirmation__isnull=False,
                allocation__registered_subject__site=stock_transfer.to_location.site,
                location=stock_transfer.from_location,
            )
        except ObjectDoesNotExist:
            skipped_codes.append(stock_code)
        else:
            with transaction.atomic():
                stock_transfer_item_model_cls.objects.create(
                    stock=stock,
                    stock_transfer=stock_transfer,
                    user_created=request.user.username,
                    created=timezone.now(),
                )
                stock.location = stock_transfer.to_location
                stock.save()
                transferred.append(stock_code)
    return transferred, skipped_codes, invalid_codes


__all__ = ["transfer_stock"]
