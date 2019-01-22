from edc_constants.constants import NEW, OPEN, CLOSED, CANCELLED

from .constants import HIGH_PRIORITY, MEDIUM_PRIORITY, LOW_PRIORITY

ACTION_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (CLOSED, "Closed"),
    (CANCELLED, "Cancelled"),
)

PRIORITY = ((HIGH_PRIORITY, "High"), (MEDIUM_PRIORITY, "Medium"), (LOW_PRIORITY, "Low"))
