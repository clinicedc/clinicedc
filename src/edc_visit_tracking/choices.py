from edc_constants.constants import (
    MISSED_VISIT, SCHEDULED, UNSCHEDULED, LOST_VISIT, DEFERRED_VISIT, COMPLETED_PROTOCOL_VISIT)

VISIT_REASON = (
    (SCHEDULED, 'Scheduled visit/contact'),
    (UNSCHEDULED, 'Unscheduled visit/contact'),
    (MISSED_VISIT, 'Missed visit'),
    (LOST_VISIT, 'Lost to follow-up (use only when taking subject off study)'),
    (DEFERRED_VISIT, 'Deferred'),
    (COMPLETED_PROTOCOL_VISIT, 'Completed protocol')
)
