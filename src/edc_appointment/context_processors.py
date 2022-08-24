from edc_visit_tracking.constants import MISSED_VISIT

from edc_appointment.constants import (
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
)


def constants(request) -> dict:
    dct = dict(
        COMPLETE_APPT=COMPLETE_APPT,
        INCOMPLETE_APPT=INCOMPLETE_APPT,
        IN_PROGRESS_APPT=IN_PROGRESS_APPT,
        MISSED_APPT=MISSED_APPT,
        MISSED_VISIT=MISSED_VISIT,
        NEW_APPT=NEW_APPT,
    )
    return dct
