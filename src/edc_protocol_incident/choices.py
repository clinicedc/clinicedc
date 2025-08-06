from edc_constants.constants import CLOSED, OPEN

from .constants import DEVIATION, VIOLATION, WITHDRAWN

DEVIATION_VIOLATION = (
    (VIOLATION, "Protocol violation"),
    (DEVIATION, "Protocol deviation"),
)

REPORT_STATUS = (
    (OPEN, "Open. Some information is still pending."),
    (CLOSED, "Closed. This report is complete"),
    (WITHDRAWN, "Withdrawn. This report has been withdrawn after review with investigators"),
)
