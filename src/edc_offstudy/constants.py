from django.conf import settings
from edc_constants.constants import DEATH_VISIT, COMPLETED_PROTOCOL_VISIT, LOST_VISIT

try:
    OFFSTUDY_REASONS = settings.OFFSTUDY_REASONS
except AttributeError:
    OFFSTUDY_REASONS = [DEATH_VISIT, COMPLETED_PROTOCOL_VISIT, LOST_VISIT]
