from edc_constants.constants import NEW, NOT_APPLICABLE, OTHER

from .constants import CANCELLED, DISPENSED, FILLED, PARTIAL

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
