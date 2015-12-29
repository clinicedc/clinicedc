from django.conf import settings

from edc_constants.constants import DEATH_VISIT, COMPLETED_PROTOCOL_VISIT, LOST_VISIT

try:
    OFF_STUDY_REASONS = settings.OFF_STUDY_REASONS
except AttributeError:
    OFF_STUDY_REASONS = [DEATH_VISIT, COMPLETED_PROTOCOL_VISIT, LOST_VISIT]
