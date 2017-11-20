from django.conf import settings

if settings.APP_NAME == 'edc_offstudy':
    from .tests import models
