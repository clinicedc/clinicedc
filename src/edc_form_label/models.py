from django.conf import settings

if settings.APP_NAME == 'edc_form_label':
    from .tests import models
