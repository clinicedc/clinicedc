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

# choices for the model, see also `get_appt_reason_choices`
DEFAULT_APPT_REASON_CHOICES = (
    (SCHEDULED_APPT, "Routine / Scheduled"),
    (UNSCHEDULED_APPT, "Unscheduled"),
)


# EDC_APPOINTMENT_ALLOW_MISSED
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

APPT_TYPE = (
    ("clinic", "In clinic"),
    ("home", "At home"),
    ("hospital", "In hospital"),
    ("telephone", "By telephone"),
)

INFO_PROVIDER = (("subject", "Subject"), ("other", "Other person"))
