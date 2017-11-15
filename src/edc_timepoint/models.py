from django.conf import settings

if settings.APP_NAME == 'edc_timepoint':
    from .tests import models
