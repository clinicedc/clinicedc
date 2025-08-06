from django.utils.translation import gettext_lazy as _
from edc_constants.constants import NOT_APPLICABLE, PATIENT

from .constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
    ONTIME_APPT,
    SCHEDULED_APPT,
    SKIPPED_APPT,
    UNSCHEDULED_APPT,
)

DEFAULT_APPT_REASON_CHOICES = (
    (SCHEDULED_APPT, _("Scheduled (study-defined)")),
    (UNSCHEDULED_APPT, _("Unscheduled / Routine")),
)

APPT_STATUS = (
    (NEW_APPT, _("Not started")),
    (IN_PROGRESS_APPT, _("In Progress")),
    (INCOMPLETE_APPT, _("Incomplete")),
    (COMPLETE_APPT, _("Done")),
    (CANCELLED_APPT, _("Cancelled")),
    (SKIPPED_APPT, _("Skipped as per protocol")),
)

APPT_TIMING = (
    (ONTIME_APPT, _("On time (within window period)")),
    (MISSED_APPT, _("Missed")),
    (NOT_APPLICABLE, _("Not applicable")),
)

INFO_PROVIDER = (
    ("subject", _("Subject")),
    ("other", _("Other person")),
)

APPT_DATE_INFO_SOURCES = (
    ("health_records", _("Health record")),
    (PATIENT, _("Patient")),
    ("estimated", _("I estimated the date")),
)
