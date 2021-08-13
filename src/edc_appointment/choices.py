from .constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
    SCHEDULED_APPT,
    UNSCHEDULED_APPT,
)
from .utils import get_appt_reason_choices

# choices for the model
DEFAULT_APPT_REASON_CHOICES = (
    (SCHEDULED_APPT, "Routine / Scheduled"),
    (UNSCHEDULED_APPT, "Unscheduled"),
)


# choices for the form and elsewhere
APPT_REASON_CHOICES = get_appt_reason_choices(DEFAULT_APPT_REASON_CHOICES)


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
