from importlib.metadata import version

__version__ = version("edc_consent")

from .exceptions import ConsentObjectDoesNotExist, NotConsentedError
from .model_wrappers import ConsentModelWrapperMixin
from .site_consents import site_consents
