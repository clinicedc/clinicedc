from django.conf import settings

if settings.APP_NAME == "edc_list_data":
    from .tests import models  # noqa
