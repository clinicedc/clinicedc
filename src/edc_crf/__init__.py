from django.conf import settings
from edc_constants.constants import INCOMPLETE

crf_status_default = getattr(settings, "CRF_STATUS_DEFAULT", INCOMPLETE)
