from importlib.metadata import version

__version__ = version("edc_dx")

from .diagnoses import Diagnoses
from .utils import (
    get_diagnosis_labels,
    get_diagnosis_labels_prefixes,
    raise_on_unknown_diagnosis_labels,
)
