from django.conf import settings

if settings.APP_NAME == 'edc_device':
    from .tests import models
