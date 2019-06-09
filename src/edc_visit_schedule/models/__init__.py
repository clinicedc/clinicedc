import sys

from django.conf import settings

from .subject_schedule_history import SubjectScheduleHistory
from .visit_schedule import VisitSchedule

if settings.APP_NAME == "edc_visit_schedule" and "makemigrations" not in sys.argv:
    from ..tests import models
