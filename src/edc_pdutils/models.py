from django.conf import settings

if settings.APP_NAME == 'edc_pdutils':
    from .tests import models
