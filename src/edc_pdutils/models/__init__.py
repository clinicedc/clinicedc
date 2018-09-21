import sys

from django.conf import settings

from .data_request import DataRequest
from .data_request_history import DataRequestHistory

if settings.APP_NAME == 'edc_pdutils' and 'makemigrations' not in sys.argv:
    from ..tests import models  # noqa
