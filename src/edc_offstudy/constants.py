from django.conf import settings
from edc_visit_tracking.constants import COMPLETED_PROTOCOL_VISIT, LOST_VISIT


try:
    OFF_STUDY_REASONS = settings.OFF_STUDY_REASONS
except AttributeError:
    OFF_STUDY_REASONS = [LOST_VISIT, COMPLETED_PROTOCOL_VISIT]
