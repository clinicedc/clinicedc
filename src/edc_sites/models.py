from django.conf import settings

if settings.APP_NAME == "edc_sites":
    from .tests.models import *  # noqa
