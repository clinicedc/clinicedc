from .constants import DEFERRED_VISIT, LOST_VISIT, MISSED_VISIT, SCHEDULED, UNSCHEDULED


def constants(request) -> dict:
    dct = dict(
        DEFERRED_VISIT=DEFERRED_VISIT,
        LOST_VISIT=LOST_VISIT,
        MISSED_VISIT=MISSED_VISIT,
        SCHEDULED=SCHEDULED,
        UNSCHEDULED=UNSCHEDULED,
    )
    return dct
