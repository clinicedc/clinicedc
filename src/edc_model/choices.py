from edc_constants.constants import OPEN, CLOSED

IDENTITY_TYPE = (
    ("OMANG", "Omang"),
    ("DRIVERS", "Driver's License"),
    ("PASSPORT", "Passport"),
    ("OMANG_RCPT", "Omang Receipt"),
    ("OTHER", "Other"),
)


REPORT_STATUS = (
    (OPEN, "Open. Some information is still pending."),
    (CLOSED, "Closed. This report is complete"),
)
