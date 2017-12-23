from django.conf import settings

from .subject_schedule_history import SubjectScheduleHistory

if settings.APP_NAME == 'edc_visit_schedule':
    from ..tests import models
