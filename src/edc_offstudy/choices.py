from edc_consent.constants import CONSENT_WITHDRAWAL
from edc_constants.constants import DEAD, OTHER
from edc_visit_tracking.constants import COMPLETED_PROTOCOL_VISIT, LOST_VISIT

OFFSTUDY_REASONS = (
    (LOST_VISIT, "Lost to follow-up"),
    (COMPLETED_PROTOCOL_VISIT, "Completed protocol"),
    (CONSENT_WITHDRAWAL, "Consent withdrawn"),
    (DEAD, "Deceased"),
    (OTHER, "Other, please specify ..."),
)
