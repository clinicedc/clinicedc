from .constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
    ONTIME_APPT,
    SCHEDULED_APPT,
    UNSCHEDULED_APPT,
)

DEFAULT_APPT_REASON_CHOICES = (
    (SCHEDULED_APPT, "Scheduled (study-defined)"),
    (UNSCHEDULED_APPT, "Unscheduled / Routine"),
)

APPT_STATUS = (
    (NEW_APPT, "Not started"),
    (IN_PROGRESS_APPT, "In Progress"),
    (INCOMPLETE_APPT, "Incomplete"),
    (COMPLETE_APPT, "Done"),
    (CANCELLED_APPT, "Cancelled"),
)

APPT_TIMING = (
    (ONTIME_APPT, "On time (within window period)"),
    (MISSED_APPT, "Missed"),
)

INFO_PROVIDER = (("subject", "Subject"), ("other", "Other person"))
