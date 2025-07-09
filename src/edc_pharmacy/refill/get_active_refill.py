from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from ..utils import get_rxrefill_model_cls

if TYPE_CHECKING:
    from ..models import Rx, RxRefill


def get_active_refill(rx: Rx) -> RxRefill | None:
    """Returns the 'active' Refill instance or None
    for this prescription.
    """
    try:
        rx_refill = get_rxrefill_model_cls().objects.get(rx=rx, active=True)
    except ObjectDoesNotExist:
        rx_refill = None
    except MultipleObjectsReturned:
        rx_refill = (
            get_rxrefill_model_cls()
            .objects.filter(rx=rx, active=True)
            .order_by("refill_start_datetime")
            .last()
        )
        get_rxrefill_model_cls().objects.filter(rx=rx, active=True).exclude(
            pk=rx_refill.pk
        ).update(active=False)
    return rx_refill
