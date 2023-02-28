from edc_constants.constants import (
    CLOSED,
    FEEDBACK,
    HIGH_PRIORITY,
    NEW,
    NORMAL,
    OPEN,
    RESOLVED,
)

from .constants import CLOSED_WITH_ACTION

RESPONSE_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (FEEDBACK, "Feedback, awaiting data manager"),
    (RESOLVED, "Resolved"),
)


DM_STATUS = (
    (OPEN, "Open, awaiting site"),
    (CLOSED, "Closed"),
    (CLOSED_WITH_ACTION, "Closed, with plan of action"),
)

QUERY_PRIORITY = ((HIGH_PRIORITY, "High"), (NORMAL, "Normal"))
