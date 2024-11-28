from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from edc_utils import get_utcnow

if TYPE_CHECKING:
    from ..models import Dispense, DispenseItem, Location, Stock


def dispense(
    stock_codes: list[str],
    location: Location,
    rx,
    dispensed_by: str,
    request: WSGIRequest,
) -> QuerySet[DispenseItem] | None:
    stock_model_cls: Type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    dispense_model_cls: Type[Dispense] = django_apps.get_model("edc_pharmacy.dispense")
    dispense_item_model_cls: Type[DispenseItem] = django_apps.get_model(
        "edc_pharmacy.dispenseitem"
    )

    assignment_mismatch = False
    for stock in stock_model_cls.objects.filter(code__in=stock_codes):
        if stock.allocation.registered_subject.subject_identifier != rx.subject_identifier:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    "Stock not allocated to subject. "
                    f"Got {stock.code}. Dispensing cancelled."
                ),
            )
            assignment_mismatch = True
            break

    if not assignment_mismatch:
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
                    created=get_utcnow(),
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
