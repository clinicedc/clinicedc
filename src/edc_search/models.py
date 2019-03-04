from django.conf import settings

if settings.APP_NAME in "edc_search":
    from .tests import models
