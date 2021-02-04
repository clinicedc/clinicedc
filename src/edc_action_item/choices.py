from edc_constants.constants import (
    CANCELLED,
    CLOSED,
    HIGH_PRIORITY,
    LOW_PRIORITY,
    MEDIUM_PRIORITY,
    NEW,
    OPEN,
)

ACTION_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (CLOSED, "Closed"),
    (CANCELLED, "Cancelled"),
)

PRIORITY = ((HIGH_PRIORITY, "High"), (MEDIUM_PRIORITY, "Medium"), (LOW_PRIORITY, "Low"))
