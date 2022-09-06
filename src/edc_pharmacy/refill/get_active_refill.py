from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from ..utils import get_rxrefill_model_cls


def get_active_refill(rx: Any) -> Any:
    """Returns the 'active' Refill instance or None
    for this prescription.

    This does not return a model instance.
    """
    try:
        rx_refill = get_rxrefill_model_cls().objects.get(rx=rx, active=True)
    except ObjectDoesNotExist:
        return None
    return rx_refill
