import sys

from django.conf import settings

from .aliquot import Aliquot
from .box import Box
from .box_item import BoxItem
from .box_type import BoxType
from .identifier_history import IdentifierHistory
from .manifest import Manifest, ManifestItem, Shipper, Consignee
from sys import argv


if settings.APP_NAME == 'edc_lab' and 'makemigrations' not in argv:
    from ..tests.models import SubjectVisit, SubjectRequisition
