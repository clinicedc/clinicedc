from edc_constants.constants import NEW, OPEN, CLOSED, CANCELLED
from edc_constants.constants import HIGH_PRIORITY, LOW_PRIORITY, MEDIUM_PRIORITY

ACTION_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (CLOSED, "Closed"),
    (CANCELLED, "Cancelled"),
)

PRIORITY = ((HIGH_PRIORITY, "High"), (MEDIUM_PRIORITY, "Medium"), (LOW_PRIORITY, "Low"))
