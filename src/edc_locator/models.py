from django.conf import settings
if settings.APP_NAME == 'edc_locator':
    from .tests import models
