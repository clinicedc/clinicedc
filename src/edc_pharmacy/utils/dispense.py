from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from ..models import Dispense, DispenseItem, Location, Stock


def dispense(
    stock_codes: list[str],
    location: Location,
    rx,
    dispensed_by: str,
    request: WSGIRequest,
) -> QuerySet[DispenseItem] | None:
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    dispense_model_cls: type[Dispense] = django_apps.get_model("edc_pharmacy.dispense")
    dispense_item_model_cls: type[DispenseItem] = django_apps.get_model(
        "edc_pharmacy.dispenseitem"
    )

    dispense_cancelled = False
    for stock in stock_model_cls.objects.filter(code__in=stock_codes):
        if stock.allocation.registered_subject.subject_identifier != rx.subject_identifier:
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock not allocated to subject. Got {stock.code}. Dispensing cancelled.",
            )
            dispense_cancelled = True
            break
        if stock.allocation.registered_subject.site.id != stock.location.site.id:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    "Stock location does not match subject's site. "
                    f"Stock item {stock.code} not at site "
                    f"{stock.allocation.registered_subject.site.id}. Dispensing cancelled."
                ),
            )
            dispense_cancelled = True
            break

    if not dispense_cancelled:
        dispense_obj = dispense_model_cls.objects.create(
            rx=rx, location=location, dispensed_by=dispensed_by
        )
        for stock in stock_model_cls.objects.filter(code__in=stock_codes):
            try:
                dispense_item_model_cls.objects.get(stock=stock)
            except ObjectDoesNotExist:
                dispense_item_model_cls.objects.create(
                    dispense=dispense_obj,
                    stock=stock,
                    user_created=request.user.username,
                    created=timezone.now(),
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Stock already dispensed. Got {stock.code}.",
                )

        return dispense_item_model_cls.objects.filter(dispense=dispense_obj)
    return None


__all__ = ["dispense"]
