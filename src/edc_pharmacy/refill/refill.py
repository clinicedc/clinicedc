from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from ..models import Rx, RxRefill


def get_active_refill(rx: Rx) -> Any:
    """Returns the 'active' Refill instance or None
    for this prescription.

    This does not return a model instance.
    """
    try:
        obj = RxRefill.objects.get(rx=rx, active=True)
    except ObjectDoesNotExist:
        return None
    return Refill(obj)


class Refill:
    """A wrapper class of the RxRefill model."""

    def __init__(self, rx_refill: RxRefill):
        self._object = rx_refill

    def __repr__(self):
        return f"{self.__class__.__name__}({self._object})"

    def __str__(self):
        return f"{self.__class__.__name__}({self._object})"

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self._object == other._object:
            return True
        return False

    @property
    def rx(self):
        return self._object.rx

    @property
    def refill_date(self):
        return self._object.refill_date

    @property
    def active(self):
        return self._object.active

    @property
    def dispensed(self):
        return self._object.dispensed

    @property
    def total(self):
        return self._object.total

    @property
    def remaining(self):
        return self._object.remaining

    def activate(self):
        """Activates this refill and deactivates the active refill
        if there is one.
        """
        if active_refill := get_active_refill(self._object.rx):
            if active_refill != self:
                active_refill.deactivate()
        self._object.active = True
        self._object.save()
        self._object.refresh_from_db()

    def deactivate(self):
        """Deactivates this refill."""
        if self._object.active:
            self._object.active = False
            self._object.save()
            self._object.refresh_from_db()
