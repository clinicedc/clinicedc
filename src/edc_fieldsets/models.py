from django.conf import settings

if settings.APP_NAME == "edc_fieldsets":
    from .tests import models
