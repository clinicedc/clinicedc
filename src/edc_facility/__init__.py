from importlib.metadata import version

__version__ = version("edc_facility")

from .facility import Facility
from .import_holidays import import_holidays
