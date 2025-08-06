from django.utils.translation import gettext as _

from edc_constants.constants import COMPLETE, NEW, NOT_APPLICABLE, OTHER

from .constants import (
    ALLOCATED,
    AVAILABLE,
    CANCELLED,
    DISPENSED,
    FILLED,
    PARTIAL,
    ZERO_ITEM,
)

PRESCRIPTION_STATUS = (
    (NEW, "New"),
    (PARTIAL, "Partially filled"),
    (FILLED, "Filled"),
    (CANCELLED, "Cancelled"),
)


DISPENSE_STATUS = ((DISPENSED, "Dispensed"), (CANCELLED, "Cancelled"))


FREQUENCY = (
    ("hr", "per hour"),
    ("day", "per day"),
    ("single", "single dose"),
    (OTHER, "Other ..."),
    (NOT_APPLICABLE, "Not applicable"),
)

ORDER_CHOICES = ((NEW, _("New")), (PARTIAL, _("Partial")), (COMPLETE, _("Complete")))

STOCK_STATUS = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (ZERO_ITEM, "Zero"),
)


STOCK_UPDATE = (
    ("edc_pharmacy.receiveitem", "Receiving"),
    ("edc_pharmacy.repackrequest", "Repacking"),
)
