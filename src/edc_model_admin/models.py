from django.conf import settings

if settings.APP_NAME == 'edc_model_admin':
    from .tests import models
