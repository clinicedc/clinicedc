from .constants import IN_PROGRESS_APPT, INCOMPLETE_APPT, COMPLETE_APPT
from .constants import SCHEDULED_APPT, UNSCHEDULED_APPT, CANCELLED_APPT, NEW_APPT

APPT_REASON = (
    (SCHEDULED_APPT, "Routine / Scheduled"),
    (UNSCHEDULED_APPT, "Unscheduled"),
)

APPT_STATUS = (
    (NEW_APPT, "New"),
    (IN_PROGRESS_APPT, "In Progress"),
    (INCOMPLETE_APPT, "Incomplete"),
    (COMPLETE_APPT, "Done"),
    (CANCELLED_APPT, "Cancelled"),
)

APPT_TYPE = (
    ("clinic", "In clinic"),
    ("home", "At home"),
    ("hospital", "In hospital"),
    ("telephone", "By telephone"),
)

INFO_PROVIDER = (("subject", "Subject"), ("other", "Other person"))
