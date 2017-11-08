from django.conf import settings

if settings.APP_NAME == 'edc_consent':
    from .tests.models import *
