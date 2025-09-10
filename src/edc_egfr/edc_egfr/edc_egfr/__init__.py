from importlib.metadata import version

__version__ = version("edc_egfr")

from .calculators import EgfrCkdEpi, EgfrCockcroftGault
