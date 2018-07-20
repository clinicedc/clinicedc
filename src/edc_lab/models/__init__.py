import sys

from django.conf import settings

from .aliquot import Aliquot
from .box import Box
from .box_item import BoxItem
from .box_type import BoxType
from .manifest import Manifest, ManifestItem, Shipper, Consignee
from .order import Order
from .panel import Panel
from .result import Result
from .result_item import ResultItem
from .model_mixins import RequisitionIdentifierMixin, RequisitionModelMixin
from .model_mixins import RequisitionStatusMixin, PanelModelError, LabProfileError

if settings.APP_NAME == 'edc_lab' and 'makemigrations' not in sys.argv:
    from ..tests.models import *
