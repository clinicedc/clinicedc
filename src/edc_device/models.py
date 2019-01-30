import sys

from django.conf import settings

if settings.APP_NAME == "edc_device" and "makemigrations" not in sys.argv:
    from .tests.models import TestModel, TestModel2, TestModelPermissions  # noqa
