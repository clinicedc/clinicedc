from django.conf import settings

from .appointment import Appointment
from .holiday import Holiday

if 'edc_appointment' in settings.APP_NAME:
    from ..tests import models
