from edc_visit_tracking.constants import COMPLETED_PROTOCOL_VISIT, LOST_VISIT
from edc_constants.constants import DEAD

from .constants import CONSENT_WITHDRAWAL

OFF_STUDY_REASONS = (
    (LOST_VISIT, 'Lost to follow-up'),
    (COMPLETED_PROTOCOL_VISIT, 'Completed protocol'),
    (CONSENT_WITHDRAWAL, 'Completed protocol'),
    (DEAD, 'Deceased'))
