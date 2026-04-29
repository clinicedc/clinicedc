from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from ..constants import TXN_DISPENSED
from ..exceptions import InvalidTransitionError
from ..transaction_log import apply_transaction

if TYPE_CHECKING:
    from ..models import Dispense, DispenseItem, Location, Stock


def dispense(
    stock_codes: list[str],
    location: Location,
    rx,
    dispensed_by: str,
    request: WSGIRequest,
) -> QuerySet[DispenseItem]:
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    dispense_model_cls: type[Dispense] = django_apps.get_model("edc_pharmacy.dispense")
    dispense_item_model_cls: type[DispenseItem] = django_apps.get_model(
        "edc_pharmacy.dispenseitem"
    )

    dispense_cancelled = False
    for stock in stock_model_cls.objects.filter(code__in=stock_codes):
        if (
            stock.current_allocation.registered_subject.subject_identifier
            != rx.subject_identifier
        ):
            messages.add_message(
                request,
                messages.ERROR,
                f"Stock not allocated to subject. Got {stock.code}. Dispensing cancelled.",
            )
            dispense_cancelled = True
            break
        if stock.current_allocation.registered_subject.site.id != stock.location.site.id:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    "Stock location does not match subject's site. "
                    f"Stock item {stock.code} not at site "
                    f"{stock.current_allocation.registered_subject.site.id}. "
                    "Dispensing cancelled."
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
                apply_transaction(
                    stock,
                    TXN_DISPENSED,
                    request.user,
                    dispense=dispense_obj,
                )
            except InvalidTransitionError:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Stock already dispensed. Got {stock.code}.",
                )

        return dispense_item_model_cls.objects.filter(dispense=dispense_obj)
    return dispense_item_model_cls.objects.none()


__all__ = ["dispense"]
