from django.conf import settings

if settings.APP_NAME == 'edc_protocol':
    from .tests import models
