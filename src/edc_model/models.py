from django.conf import settings

if settings.APP_NAME == "edc_model":
    from .tests.models import *  # noqa
