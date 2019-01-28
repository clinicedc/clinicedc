from django.conf import settings

if settings.APP_NAME == "edc_subject_dashboard":
    from .tests import models  # noqa
