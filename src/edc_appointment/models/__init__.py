import sys

from django.conf import settings

from .appointment import Appointment

if 'edc_appointment' in settings.APP_NAME and 'makemigrations' not in sys.argv:
    from ..tests import models
