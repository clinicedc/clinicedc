import sys

from django.apps import apps as django_apps
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


def get_requisition_model():
    return django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)


def get_panel_model_cls():
    return django_apps.get_model("edc_lab.panel")


if settings.APP_NAME == "edc_lab" and "makemigrations" not in sys.argv:
    from ..tests.models import *
